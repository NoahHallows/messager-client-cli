from client_backend import ChatClient
import threading
import sys

class ChatClientCLI:
    def __init__(self):
        self.client = ChatClient()
        self.input_lock = threading.Lock()

    def message_handler(self, message):
        # Handle incomming messages
        with self.input_lock:
            # Clear current line
            sys.stdout.write('\r' + ' '*50 + '\r')
            # Print the message
            print(f"Recived: {message}")
            # Redisplay the input line
            sys.stdout.write("Enter your message: ")
            sys.stdout.flush()

    def send_message_loop(self):
        # Loop for sending messages
        while True:
            with self.input_lock:
                message = input("Enter your message: ")

            if message.lower() == ":q":
                print("Exiting...")
                self.client.disconnet()
                break
            if not self.client.send_message(message):
                print("Failed to send message, connection may be lost")
                break

    def login_prompt(self):
        while True:
            username = input("Enter your username: ")
            if username.lower() == ":q":
                return False

            password = input("Enter your password: ")
            success, message = self.client.login(username, password)
            print(message)

            if success:
                return True

    def create_account_prompt(self):
        while True:
            username = input("Enter your username: ")
            if username.lower() == ":q":
                return False

            password = input("Enter your password: ")

            success, message = self.client.create_account(username, password)
            print(message)

            if success:
                return True

    def run(self):
        # Main entry point for cli client
        print("=== Quack message ===")

        # Connect to server
        print(f"Connecting to server...")
        if not self.client.connect():
            print("Failed to connect to server. Exiting.")
            return
        
        print("Connected to server")

        # Login or create account
        choice = input("Do you want to create a new account? (y/n)")
        if choice.lower() == 'y':
            authenticated = self.create_account_prompt()
        else:
            authenticated = self.login_prompt()

        if not authenticated:
            print("Authentication cancelled. Exiting.")
            self.client.disconnet()
            return

        # Set up message handling
        self.client.set_message_callback(self.message_handler)
        self.client.start_receiving()

        # Start the message sending Loop
        try:
            self.send_message_loop()
        except KeyboardInterrupt:
            print("\nExiting...")
        finally:
            self.client.disconnect()

if __name__ == "__main__":
    cli = ChatClientCLI()
    cli.run()
