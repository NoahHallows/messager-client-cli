import socket
import threading
import bcrypt

HOST = "127.0.0.1"
PORT = 28752
shutdown = False

def send_message(s):
    while True:
        message = input("Enter your message: ")
        if message == ":q":
            break
        s.sendall(message.encode())

def recive_message(s):
    while True:
        if shutdown:
            break
        data = s.recv(1024)
        if not data:
            break
        print(f"Recived {data.decode()}")

def login(s):
    while True:
        username = input("Enter your username: ")
        if username == ":q":
            s.sendall("\0".encode())
            break
        password = input("Enter your password: ")
        s.sendall(username.encode())
        data = s.recv(1024)
        if data.decode().strip() != "False":
            salt = data.decode().strip()
            password_hash = bcrypt.hashpw(password.encode(), salt.encode())
            s.sendall(password_hash)
            data = s.recv(1024)
            logined = data.strip()
            if logined == b'1':
                print("Successful login")
                return username, password_hash
            else:
                print("Incorrect username or password")
                salt = None
                continue
        else:
            print("Incorrect username or password")
            salt = None
            continue


def main():
    global shutdown
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((HOST, PORT))
    username, password_hash = login(s)
    send_message_thread = threading.Thread(target=send_message, args=(s, ))
    recive_message_thread = threading.Thread(target=recive_message, args=(s, ), daemon=True)
    send_message_thread.start()
    recive_message_thread.start()
    send_message_thread.join()
    shutdown = True

    print("Finished")
    exit()

main()
