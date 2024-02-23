from library.jmod import jmod, data_tables
import re, os

settings_file = 'settings.json'

colours = {
    "red": "\033[91m",
    "green": "\033[92m",
    "yellow": "\033[93m",
    "blue": "\033[94m",
    "purple": "\033[95m",
    "cyan": "\033[96m",
    "white": "\033[97m",
}

class userman:
    '''
    User management class.
    '''
    def CLI():
        '''
        Command Line Interface for user management.
        '''
        while True:
            print(f"{colours['green']}UserManagement{colours['white']}: Type 'help' for a list of commands.")
            command = input(">>> ").lower()
            args = command.split(" ")[1:]
            command = command.split(" ")[0]

            if len(args) == 0:
                # Pads the arguments with "None" to avoid index errors
                args = [None, None, None, None, None, None]

            if command == "0" or command == "exit":
                print("Exiting user management.")
                break
            elif command == "1" or command == "add":
                userman.add_user(args[0], args[1], args[2], args[3])
            elif command == "2" or command == "remove":
                userman.remove_user(args[0])
            elif command == "3" or command == "edit":
                userman.edit_user(args[0])
            elif command == "4" or command == "list":
                userman.list_users(for_cli=True)
            elif command == "5" or command == "help":
                userman.print_help_msg()
            elif command == "":
                continue
            else:
                print("Invalid command. Please try again.")
                continue

    def add_user(username=None, password=None, homedir=None, perm=None) -> None:
        '''
        Adds a user to the FTP server.

        Args:
            username: The username of the user.
            password: The password of the user.
            homedir: The home directory of the user.
            perm: The permissions of the user.
        '''
        try:
            if username == None:
                username = userman.get_data.username()
            if password == None:
                password = userman.get_data.password()
            if homedir == None:
                homedir = userman.get_data.homedir()
            if perm == None:
                perm = userman.get_data.perms()
        except KeyboardInterrupt:
            print("Cancelling user creation.")
            return
        
        user_dt = data_tables.NEW_USER_DT(username, password, perm, homedir)
        user_list = userman.list_users()
        user_list[username] = user_dt

        jmod.setvalue(
            key=f"PyTrain_users",
            value=user_list,
            json_dir=settings_file,
            dt=data_tables.SETTINGS_DT,
        )
        print(f'{colours["green"]}User added successfully.{colours["white"]}')

    def remove_user(username=None) -> None:
        '''
        Removes a user from the FTP server.

        Args:
            username: The username of the user to remove.
        '''
        if username == None:
            try:
                username = userman.get_data.username(only_existing=True)
            except KeyboardInterrupt:
                print("Cancelling user removal.")
                return
            
        user_list = userman.list_users()
        del user_list[username]

        jmod.setvalue(
            key=f"PyTrain_users",
            value=user_list,
            json_dir=settings_file,
            dt=data_tables.SETTINGS_DT,
        )
        print(f'{colours["green"]}User removed successfully.{colours["white"]}')
    
    def edit_user(username=None) -> None:
        '''
        Edits a user on the FTP server.

        Args:
            username: The username of the user to edit.
        '''
        if username == None:
            try:
                username = userman.get_data.username(only_existing=True)
            except KeyboardInterrupt:
                print("Cancelling user editing.")
                return
        
        user_list = userman.list_users()
        user = user_list[username]

        processed_homedir = str(user['home_dir'])
        # Determines if the homedir is an absolute path or a local user directory
        if os.path.isabs(processed_homedir) is False:
            # Likely a local user directory
            processed_homedir = f"~/{processed_homedir}"

        acceptables = ["username", "homedir", "perm", "password"]
        while True:
            try:
                print(f"Editing user '{username}'")
                print(f"Current home directory: {processed_homedir}")
                print(f"Current permissions: {user['permissions']}")
                print('Type "password" to reveal/change the password.')
                print('\nWhich field would you like to edit? (username/homedir/perm/password)')
                field = input(">>> ").lower()
                if field not in acceptables:
                    print("Invalid field. Please try again.")
                    continue

                if field == "password":
                    print(f"Current password: {user['password']}")
                    command = input("Would you like to change the password? (y/n) ").lower()
                    if "y" in command:
                        print("Enter the new password.")
                        user['password'] = userman.get_data.password()
                    else:
                        print("Password not changed.")
                elif field == "homedir":
                    print("Enter the new home directory.")
                    user['home_dir'] = userman.get_data.homedir()
                elif field == "perm":
                    print("Enter the new permissions.")
                    user['permissions'] = userman.get_data.perms()
                elif field == "username":
                    del user_list[username]
                    print("Enter the new username.")
                    username = userman.get_data.username()
                    user_list[username] = user
                    user_list[username]['username'] = username
                else:
                    print("Invalid field. Please try again.")
                    continue
            except KeyboardInterrupt:
                print("Would you like to save the changes? (y/n)")
                command = input(">>> ").lower()
                if command in ["y", "yes", ""]: # Default to yes
                    jmod.setvalue(
                        key=f"PyTrain_users",
                        value=user_list,
                        json_dir=settings_file,
                        dt=data_tables.SETTINGS_DT,
                    )
                    print(f'{colours["green"]}User edited successfully.{colours["white"]}')
                    return True
                else:
                    print("Changes not saved.")
                    return False

    def list_users(for_cli=False) -> dict:
        '''
        Lists all users on the FTP server.

        Args:
            for_cli: Whether to print the users to the console.

        Returns:
            list: A list of all users on the FTP server.
        '''
        user_list = jmod.getvalue(
            key='PyTrain_users',
            json_dir=settings_file,
            default={},
            dt=data_tables.SETTINGS_DT
        )
        if for_cli:
            for user in user_list:
                user: dict = user_list[user]
                print(f"Username: {user['username']}")
                print(f"Home directory: {user['home_dir']}")
                print(f"Permissions: {user['perm']}")
                print()
        return user_list

    def print_help_msg():
        '''
        Prints the help message for user management.
        '''
        print("User Management Help:")
        print("0. Exit: Exits user management.\n")
        print("1. Add user: Adds a user to the FTP server.")
        print("Arguments: username, password, homedir, perm.\n")
        print("2. Remove user: Removes a user from the FTP server.")
        print("Arguments: username.\n")
        print("3. Edit user: Edits a user on the FTP server.")
        print("Arguments: username.\n")

        print("4. List users: Lists all users on the FTP server.")
        print("5. Help: Prints this help message.")

    class get_data:
        '''
        Class that contains methods for getting user data.
        Raises KeyboardInterrupt if the user cancels the input.
        '''
        def username(only_existing=False):
            while True:
                username = str(input("Enter the username: "))
                if username == "cancel":
                    print("'cancel' is a forbidden username. Did you want to leave the user creation process? (y/n)")
                    if "y" in input(">>> ").lower():
                        raise KeyboardInterrupt
                elif username == "":
                    print("Username cannot be empty.")
                    continue
                # A RE for allow numbers, letters, and underscores with a length of 3-20 characters and allow full stops (periods)
                elif not re.match("^[a-zA-Z0-9_.]{3,20}$", username):
                    print("Invalid username. Please try again.")
                    print("Username must be 3-20 characters long and can only contain letters, numbers, full stops (periods) and underscores.")
                    continue
                elif " " in username:
                    print("Username cannot contain spaces.")
                    continue
                else:
                    if only_existing is True:
                        if username in dict(jmod.getvalue(json_dir=settings_file, dt=data_tables.SETTINGS_DT, key="PyTrain_users", default={})).keys():
                            return username
                        else:
                            print("The specified user does not exist.")
                            continue
                    else:
                        if username in dict(jmod.getvalue(json_dir=settings_file, dt=data_tables.SETTINGS_DT, key="PyTrain_users", default={})).keys():
                            print("The specified user already exists. Please try again.")
                            continue
                    return username
                
        def password():
            while True:
                password = str(input("Enter the password: "))
                if password == "cancel":
                    raise KeyboardInterrupt
                elif password == "":
                    print("Password cannot be empty.")
                    continue
                elif len(password) < 4:
                    print("Password must be at least 6 characters long.")
                    continue
                else:
                    return password

        def homedir():
            while True:
                print("Hint: Use the '~' character to append the project directory to the specified folder.")
                print("And enter 'local' for a homedir of the same name as the user.")
                homedir = str(input("Enter the home directory: "))
                
                if homedir == "cancel":
                    raise KeyboardInterrupt
                elif homedir == "local":
                    return "<>local_user<>"
                elif homedir == "":
                    print("Home directory cannot be empty.")
                    continue
                elif homedir.startswith("~"):
                    print("Appendng the current working directory to the specified folder...")
                    homedir = os.path.join(os.getcwd(), homedir[1:])

                if not os.path.exists(homedir):
                    print("The specified directory does not exist. Please try again or enter an absolute (full) path.")
                    continue

                else:
                    return homedir
                
        def perms(askToSave=True):
            # Start an infinite loop
            while True:
                # Define permission sets
                read_perms = "elr"
                read_write_perms = "elradfmw"
                admin_perms = "elradfmwMT"

                # Print the link to the documentation and ask the user to choose between preset and custom permissions
                print("https://pyftpdlib.readthedocs.io/en/latest/api.html#control-connection")
                print("Do you want to use a preset or custom permissions? (preset/custom)")
                perm_type = input(">>> ").lower()
                # If the user types "cancel", raise a KeyboardInterrupt
                if perm_type == "cancel":
                    raise KeyboardInterrupt
                # If the user types anything other than "preset" or "custom", inform them that their choice is invalid and ask again
                elif not perm_type in ["preset", "custom"]:
                    print("Invalid choice. Please try again.")
                    continue
                else:
                    break

            # Define a dictionary mapping permission codes to their descriptions
            perms_match = {
                "e": "change directory",
                "l": "list files",
                "r": "retrieve file",
                "a": "append data to file",
                "d": "delete file",
                "f": "rename file",
                "m": "create directory",
                "w": "store file",
                "M": "change file mode",
                "T": "change file modification time",
            }

            # Start another infinite loop
            while True:
                # If the user chose "preset" permissions, present them with three options
                if perm_type == "preset":
                    askToSave = False
                    print("Preset permissions:")
                    print(f"1. Read only ({read_perms})")
                    print(f"2. Read Write ({read_write_perms})")
                    print(f"3. Admin ({admin_perms})")
                    perm_choice = input(">>> ").lower()
                    # If the user types "1" or "read only", set the permissions to read_perms and break the loop
                    if perm_choice == "1" or perm_choice == "read only":
                        perm = read_perms
                        break
                    # If the user types "2" or "read write", set the permissions to read_write_perms and break the loop
                    elif perm_choice == "2" or perm_choice == "read write":
                        perm = read_write_perms
                        break
                    # If the user types "3" or "admin", set the permissions to admin_perms and break the loop
                    elif perm_choice == "3" or perm_choice == "admin":
                        perm = admin_perms
                        break
                    elif perm_choice == "cancel":
                        raise KeyboardInterrupt
                    else:
                        print("Invalid choice. Please either options 1, 2 or 3 only.")
                        continue
                # If the user chose "custom" permissions, ask them to enter the permissions they want to use
                elif perm_type == "custom":
                    print("READ THE DOCS: https://pyftpdlib.readthedocs.io/en/latest/api.html#control-connection")

                    # Get the saved permission sets
                    saved_sets = jmod.getvalue(
                        key="permission_sets",
                        json_dir=settings_file,
                        dt=data_tables.SETTINGS_DT,
                        default={}
                    )
                    compare_sets = {}
                    for perm_set in saved_sets:
                        compare_sets[f'<{perm_set}>'] = saved_sets[perm_set]["permissions"]
                        
                    # If there are no saved permission sets, inform the user
                    if len(saved_sets) == 0:
                        print(f"{colours['yellow']}No saved permission sets found.{colours['white']}")
                    else:
                        print(f"{colours['green']}Saved permission sets:{colours['white']}")
                        
                        # Print the saved permission sets
                        counter = 0
                        for perm_set in saved_sets:
                            # permset would be the key in this case. saved_sets[perm_set] would be the value
                            name, desc, permission = saved_sets[perm_set]['name'], saved_sets[perm_set]['description'], saved_sets[perm_set]['permissions']
                            # If the counter is even, set the text colour to white. If it's odd, set the text colour to gray
                            grayed = "" if counter % 2 == 0 else "\033[90m"
                            print(f"{grayed}<{name}> : {desc} ({permission}){colours['white']}")
                            counter += 1
                        print()

                    # Ask the user to enter the permissions they want to use
                    print("Enter the permissions you want to use. (e.g. elradfmw)")
                    if len(saved_sets) != 0:
                        print("or use an old perm set by typing its above listed name. eg, <project x people>")
                    perm = input(">>> ").lower()
                    # If the user types "cancel", raise a KeyboardInterrupt
                    if perm == "cancel":
                        raise KeyboardInterrupt
                    elif perm.startswith("<") and perm.endswith(">"):
                        if perm in compare_sets.keys():
                            print(f"Selected permission set {perm}")
                            perm = compare_sets[perm]
                            askToSave = False
                            break
                        else:
                            print("Invalid permission set name. Please try again.")
                            continue
                    # If the user types a string that doesn't match the regular expression "^[elradfmw]{1,7}$", inform them that their choice is invalid and ask again
                    elif not re.match("^[elradfmw]{1,7}$", perm):
                        print("Invalid permissions. Please try again.")
                        continue
                    else:
                        # If the user's custom permissions are valid, print out the descriptions of the permissions they chose and ask them to confirm
                        print(f"{colours['green']}This permissions set will be{colours['white']}")
                        counter = 0
                        for i in perm:
                            grayed = "" if counter % 2 == 0 else "\033[90m"
                            print(f"{grayed}{perms_match[i]}: {i}{colours['white']}")
                            counter += 1
                        print("Is this correct? (y/n)")
                        command = input(">>> ").lower()
                        # If the user confirms, break the loop
                        if "y" in command:
                            break
                        else:
                            print("Please try again.")
                            continue

            # If the askToSave flag is set to True
            if askToSave:
                # Start an infinite loop
                while True:
                    # Ask the user if they want to save the permission set
                    print("Would you like to save this permission set? (y/n)")
                    command = input(">>> ").lower()
                    # If the user types "y" or "n", break the loop
                    if 'y' in command or 'n' in command:
                        break
                    else:
                        # If the user types anything else, inform them that their choice is invalid and ask again
                        print("Invalid choice. Please try again.")
                        continue

                # If the user wants to save the permission set
                if "y" in command:
                    # Initialize a new permission set
                    perm_set = data_tables.PERMISSION_SET
                    perm_set["permissions"] = perm

                    # Start an infinite loop
                    while True:
                        # Ask the user to enter a name for the permission set
                        print("Enter a name for the permission set.")
                        perm_set["name"] = input(">>> ")
                        # If the user types "cancel", raise a KeyboardInterrupt
                        if perm_set["name"] == "cancel":
                            raise KeyboardInterrupt
                        elif perm_set["name"] == "":
                            print("Name cannot be empty.")
                            continue
                        else:
                            break

                    # Start another infinite loop
                    while True:
                        # Ask the user to enter a description for the permission set
                        print("How would you describe this permission set? (e.g. 'read only' or 'for admins')")
                        perm_set["description"] = input(">>> ")
                        if perm_set["description"] == "cancel":
                            raise KeyboardInterrupt
                        # If the user doesn't enter a description, inform them that the description cannot be empty and ask again
                        elif perm_set["description"] == "":
                            print("Description cannot be empty.")
                            continue
                        else:
                            break

                    saved_perm_sets = jmod.getvalue(
                        key="permission_sets",
                        json_dir=settings_file,
                        dt=data_tables.SETTINGS_DT,
                        default={}
                    )
                    # Add the new permission set to the saved permission sets
                    saved_perm_sets[perm_set["name"]] = perm_set
                    # Save the updated permission sets
                    jmod.setvalue(
                        key="permission_sets",
                        value=saved_perm_sets,
                        json_dir=settings_file,
                        dt=data_tables.SETTINGS_DT,
                    )
                    print(f"{colours['green']}Permission set saved successfully.{colours['white']}")

            # Return the permissions the user chose
            return perm