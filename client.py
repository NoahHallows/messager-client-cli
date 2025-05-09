import socket
import threading

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

def main():
    global shutdown
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((HOST, PORT))
    send_message_thread = threading.Thread(target=send_message, args=(s, ))
    recive_message_thread = threading.Thread(target=recive_message, args=(s, ), daemon=True)
    send_message_thread.start()
    recive_message_thread.start()
    send_message_thread.join()
    shutdown = True

    print("Finished")
    exit()

main()
