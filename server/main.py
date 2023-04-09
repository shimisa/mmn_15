import socket
import threading
import socketserver


def client(ip, port, message):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((ip, port))
        sock.sendall(bytes(message, 'ascii'))
        response = str(sock.recv(1024), 'ascii')
        print("Received: {}".format(response))


if __name__ == "__main__":
    portInfo = open("port.info", "r")
    # Port 0 means to select an arbitrary unused port
    ip, port = "localhost", int(portInfo.read())

    client(ip, port, "Hello World 1")
    client(ip, port, "Hello World 2")
    client(ip, port, "Hello World 3")
    client(ip, port, "Hello World 3")
    client(ip, port, "Hello World 3")
    client(ip, port, "Hello World 3")


        # server.shutdown()