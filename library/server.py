from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives import hashes
from library.jmod import jmod, data_tables
from cryptography.x509.oid import NameOID
from cryptography import x509
import multiprocessing
import datetime
import logging
import time
import ssl
import os

from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import ThreadedFTPServer

settings_file = "settings.json"

def generate_ssl(certfile_dir, keyfile_dir, hostname="localhost"):
    # Generate a self-signed certificate if it doesn't exist
    if not os.path.isfile(certfile_dir) or not os.path.isfile(keyfile_dir):
        key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
        )
        os.makedirs(os.path.dirname(certfile_dir), exist_ok=True)

        name = x509.Name([
            x509.NameAttribute(NameOID.COMMON_NAME, u"{}".format(hostname)),
        ])

        cert = x509.CertificateBuilder().subject_name(
            name
        ).issuer_name(
            name
        ).public_key(
            key.public_key()
        ).serial_number(
            x509.random_serial_number()
        ).not_valid_before(
            datetime.datetime.utcnow()
        ).not_valid_after(
            datetime.datetime.utcnow() + datetime.timedelta(days=365)
        ).sign(key, hashes.SHA256())

        # Write our certificate out to disk.
        with open(certfile_dir, "wb") as f:
            f.write(cert.public_bytes(serialization.Encoding.PEM))

        # Write our key out to disk
        with open(keyfile_dir, "wb") as f:
            f.write(key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.TraditionalOpenSSL,
                encryption_algorithm=serialization.NoEncryption(),
            ))

class ftps:
    def run():
        # Starts the FTP server in a thread
        THREAD = multiprocessing.Process(
            target=ftps.main,
            name="FTPServer"
        )
        THREAD.start()
        try:
            time.sleep(0.5)
        except:
            pass
        return THREAD

    def main(use_ssl=True, prvkeyfile=None, certfile=None):
        '''
        Not intended to be run as a standalone script. use ftps.run() instead.
        This is a FTP server using pyftpdlib.
        '''
        if use_ssl:
            # Paths to the certificate and key files
            certfile = 'library/ssl/certificate.pem' if certfile is None else certfile
            keyfile = 'library/ssl/private.key' if prvkeyfile is None else prvkeyfile
            ssl_exist = {
                "prv": os.path.isfile(certfile),
                "cert": os.path.isfile(certfile),
                }
            os.makedirs("library/ssl/", exist_ok=True)
            if not ssl_exist["prv"] or not ssl_exist["cert"]:
                generate_ssl(certfile, keyfile)

        root_password = jmod.getvalue(
            key='RootPassword',
            json_dir=settings_file,
            default='password',
            dt=data_tables.SETTINGS_DT
        )

        authorizer = DummyAuthorizer()
        authorizer.add_user("root", root_password, homedir=".", perm="elradfmw")
        # Expecting a list of dicts with the following keys: username, password, ftp_dirs, perm
        user_list = jmod.getvalue(
            key='PyTrain_users',
            json_dir=settings_file,
            default={},
            dt=data_tables.SETTINGS_DT
        )
        for user in user_list:
            user: dict = user_list[user]

            # Adds the user to the authorizer
            authorizer.add_user(
                user['username'],
                user['password'],
                homedir=user['home_dir'],
                perm=user['perm']
            )

        ftpAnonAllowed = jmod.getvalue(
            key='AnonAllowed',
            json_dir=settings_file,
            default=False,
            dt=data_tables.SETTINGS_DT
        )
        if ftpAnonAllowed:
            authorizer.add_anonymous(".", perm="elr")

        connected_users = []
        class MyFTPHandler(FTPHandler):
            """
            Custom FTP handler class that extends the FTPHandler class.

            Attributes:
                None

            Methods:
                on_connect(): Method called when a client connects to the FTP server. It logs the IP address, port, and whether the connection is secure.
            """
            def on_connect(self):
                """
                Method called when a client connects to the FTP server.

                It logs the IP address, port, and whether the connection is secure.
                """
                is_secure = self.ssl_context is not None
                # Gets which account is logging in and sets it in the json file
                logging.info(f"IP \"{self.remote_ip}\" with username \"{self.username}\" has connected on Port \"{self.remote_port}\". Secure: {is_secure}")

            def on_login(self, username):
                connected_users.append(username)

            def on_logout(self, username): # Does not count on disconnect. gotta time them out
                connected_users.remove(username)

            def get_connected_users(cls):
                return list(connected_users)

        handler = MyFTPHandler
        handler.authorizer = authorizer

        if use_ssl:
            # Create an SSL context and assign it to the handler
            ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
            ssl_context.load_cert_chain(certfile=certfile, keyfile=keyfile)
            handler.ssl_context = ssl_context

            handler.tls_control_required = True  # Require TLS for control connection
            handler.tls_data_required = True  # Require TLS for data connection

        server_port = jmod.getvalue(
            key='port',
            json_dir=settings_file,
            default=6464,
            dt=data_tables.SETTINGS_DT
        )
        server = ThreadedFTPServer(("localhost", server_port), handler)
        print(f"<--FILE TRANSFER PROTOCAL {'SECURED' if use_ssl else ''} RUNNING ON \"localhost:{server_port}\" WITH {len(user_list)} USERS-->", flush=True)

        try:
            while True:
                server.serve_forever(blocking=False)
                # Updates user list
                user_list = jmod.getvalue(
                    key='PyTrain_users',
                    json_dir=settings_file,
                    dt=data_tables.SETTINGS_DT,
                    default={}
                )

                # Updates the authorizer
                for user in user_list:
                    user: dict = user_list[user]

                    # Checks if the user is already in the authorizer
                    if user['username'] not in authorizer.user_table:
                        # Adds the user to the authorizer
                        authorizer.add_user(
                            user['username'],
                            user['password'],
                            homedir=user['home_dir'],
                            perm=user['perm']
                        )
                    # If they are not in the json file but are in the authorizer, remove them
                    if user['username'] in authorizer.user_table and user['username'] not in user_list:
                        authorizer.remove_user(user['username'])

        except KeyboardInterrupt:
            server.close_all()
            print("--FILE TRANSFER PROTOCAL HAS BEEN STOPPED--")