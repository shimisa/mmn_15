import socket
import sys

IP = socket.gethostbyname(socket.gethostname())
# IP = "localhost"
PORT = 80
ADDR = (IP, PORT)
BUFF_SIZE = 1024
FORMAT = "utf-8"
DISCONNECT_MSG = "!DISCONNECT"


def main():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(ADDR)
    print(f"[CONNECTED] Client connected to server at {IP}:{PORT}")

    connected = True
    while connected:
        msg = input("> ")
        msg = client.send(msg.encode(FORMAT))

        if msg == DISCONNECT_MSG:
            connected = False
        else:
            msg = client.recv(BUFF_SIZE).decode(FORMAT)
            print(f"[SERVER] {msg}")


if __name__ == "__main__":
    main()
