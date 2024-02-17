import sentry_sdk as sentry
sentry.init(
    dsn="https://ae6f5c44a2035014c194291036202913@o4506723665313792.ingest.sentry.io/4506757166727168",
    # Set traces_sample_rate to 1.0 to capture 100%
    # of transactions for performance monitoring.
    traces_sample_rate=1.0,
    # Set profiles_sample_rate to 1.0 to profile 100%
    # of sampled transactions.
    # We recommend adjusting this value in production.
    profiles_sample_rate=1.0,
)
import os
os.makedirs("library/ssl/", exist_ok=True)
from library.server import ftps

colours = {
    "red": "\033[91m",
    "green": "\033[92m",
    "yellow": "\033[93m",
    "blue": "\033[94m",
    "purple": "\033[95m",
    "cyan": "\033[96m",
    "white": "\033[97m",
    "end": "\033[0m"
}

class PyTrain:
    def main() -> None:
        """
        Main function that starts the FTP server and handles user commands.
        """
        # Starts the FTP server in a thread
        FTPS_THREAD = ftps.run()

        # Main loop
        while True:
            try:
                print("Welcome to PyTrain: Sending your files on the fast track! Type 'help' for a list of commands.")
                command = input(f"{colours['green']}>>>{colours['end']} ")
                if command == "exit":
                    command = input("Are you sure you want to exit? This will shut down all FTPS servers. (y/n): ")
                    if "y" in command:
                        raise KeyboardInterrupt
                    else:
                        print("Continuing to run.")
                elif command == "cls":
                    os.system("cls" if os.name == "nt" else "clear")
                    continue
                elif command == "help":
                    PyTrain.print_help_msg()
                elif command == "":
                    continue # Captures empty input
                else:
                    print(f"{colours['yellow']}Invalid command. Please try again.{colours['end']}")
                print("\n")
            except KeyboardInterrupt:
                print("Exiting. Thank you for using PyTrain!")
                FTPS_THREAD.kill()
                exit()

    def print_help_msg():
        print("Commands:")
        print("exit - Exits the program")
        print("cls - Clears the console")
        print("help - Displays this message")

if __name__ == "__main__":
    PyTrain.main()