import socket
import threading
import bcrypt
from time import sleep
import json
import struct

VERSION = "1.0"
#HOST="127.0.0.1"
HOST="messager.quackmail.com.au"
PORT = 28752

class ChatClient:
    def __init__(self, host=HOST, port=PORT):
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

    def version_check(self):
        server_version = self.socket.recv(1024).decode()
        if server_version == VERSION:
            return True
        else:
            return False


    def set_message_callback(self, callback):
        # Set callback function for receiving messages
        self.message_callback = callback

    def start_receiving(self):
        # Start the message receiving threading
        self.receive_thread = threading.Thread(target=self._receive_message, daemon=True)
        self.receive_thread.start()
    
    def _recv_all(self, n):
        buf = b""
        while len(buf) < n:
            chunk = self.socket.recv(n - len(buf))
            if not chunk:
                raise ConnectionError("Server disconnected")
            buf += chunk
        return buf

    def _receive_message(self):
        # Background process to receive messages
        while not self.shutdown:
            try:
                # 1) read exactly 4 bytes for the length header
                raw_len = self._recv_all(4)
                msg_len = struct.unpack("!I", raw_len)[0]
                # 2) now read exactly msg_len bytes of JSON
                data = self._recv_all(msg_len)
                # 2) read the JSON payload

                # 3) parse JSON
                payload = json.loads(data.decode("utf-8"))
                sender  = payload["sender"]
                message = payload["message"]
                if self.message_callback:
                    self.message_callback(message, sender)
                else:
                    print(f"{sender}: {message} CALLBACK IS NOT WORKING!!!!")
            except Exception as e:
                print(f"Reveive message error: {e}")
                if not self.shutdown:
                    break

    def send_message(self, message):
        try:
            # 1) build a dict
            payload = {
                "sender":   self.username,
                "message":  message
            }
            # 2) convert to UTF-8 JSON bytes
            data = json.dumps(payload).encode("utf-8")
            # 3) prefix with 4-byte big-endian length
            header = struct.pack("!I", len(data))
            # 4) send header + body
            self.socket.sendall(header + data)
            return True
        except Exception as e:
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
            response = data.strip()

            if response == "False":
                return False, "Incorrect username or password"

            # Hash password
            salt = response
            password_hash = bcrypt.hashpw(password.encode(), salt)

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
            # Check if username is avalible`
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
            return False, f"Account creation error: {e}"
