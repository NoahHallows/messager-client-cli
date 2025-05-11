import socket
import threading
import bcrypt
from time import sleep

class ChatClient:
    def __init__(self, host="127.0.0.1", port=28752):
        self.host = host
        self.port = port
        self.socket = None
        self.username = None
        self.password_hash = None
        self.shutdown = None
        self.message_callback = None

    def connect(self):
        # Establish connection to server
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.host, self.port))
            return True
        except Exception as e:
            print(f"Connection error: {e}")
            return False

    def disconnect(self):
        # Disconnect from server
        if self.socket:
            self.socket.close()
        self.shutdown = True

    def set_message_callback(self, callback):
        # Set callback function for reciving messages
        self.message_callback = callback

    def start_receiving(self):
        # Start the message reciving threading
        self.recive_thread = threading.Thread(target=self._receive_message, daemon=True)
        self.recive_thread.start()

    def _receive_message(self):
        # Background process to recive messages
        while not self.shutdown:
            try:
                data = self.socket.recv(1024)
                if not data:
                    break
                message = data.decode()
                if self.message_callback:
                    self.message_callback(message)
                else:
                    print(f"Recived: {message}")
            except Exception as e:
                if not self.shutdown:
                    print(f"Error reciving message: {e}")
                break

    def send_message(self, message):
        # Send message to server
        try:
            self.socket.sendall(message.encode())
            return True
        except Exception as e:
            print(f"Error sending message: {e}")
            return False

    def login(self, username, password):
        # Login function
        try:
            self.socket.sendall("login".encode())
            sleep(0.5)
            # Send username
            self.socket.sendall(username.encode())
            # Get salt
            data = self.socket.recv(1024)
            response = data.decode().strip()

            if response == "False":
                return False, "Incorrect username or password"

            # Hash password
            salt = response
            password_hash = bcrypt.hashpw(password.encode(), salt.encode())

            # Send hashed password
            self.socket.sendall(password_hash)
            
            # Get result
            data = self.socket.recv(1024)
            if data.strip() == b'1':
                self.username = username
                self.password_hash = password_hash
                return True, "Login successful"
            else:
                return False, "Incorrect username or password"

        except Exception as e:
            return False, f"Login error: {e}"

    def create_account(self, username, password):
        # Create new account
        try:
            self.socket.sendall("newaccount".encode())
            sleep(0.5)
            # Send username
            self.socket.sendall(username.encode())
            # Check if username is avalible
            data = self.socket.recv(1024)
            if data.strip() != b'0':
                return False, "Username already taken"
            
            # Generate password
            salt = bcrypt.gensalt()
            password_hash = bcrypt.hashpw(password.encode(), salt)

            # Send hashed password and salt
            self.socket.sendall(password_hash)
            self.socket.sendall(salt)

            data = self.socket.recv(1024)
            if data.strip() == b'1':
                self.username = username
                self.password_hash = password_hash
                return True, f"User {username} created successfully"
            else:
                return False, "Error creating account"

        except Exception as e:
            return False, "Account creation error: {e}"
