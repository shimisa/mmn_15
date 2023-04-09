import socket
import threading
import dao
import controller
import time


class Server:
    _dao = dao.dao_service
    IP = "127.0.0.1"
    # IP = "localhost"
    PORT = 1234
    ADDR = (IP, PORT)
    BUFF_SIZE = 5000
    FORMAT = "utf-8"
    DISCONNECT_MSG = "!DISCONNECT"
    controller = controller.Controller()

    def handle_client(self, conn, addr):
        print(f"[NEW CONNECTION] {addr} connected.")
        connected = True
        while connected:
            msg = conn.recv(self.BUFF_SIZE)
            encoded_msg = ""
            try:
                encoded_msg = msg.decode(self.FORMAT)
            except UnicodeDecodeError:
                encoded_msg = encoded_msg.join(map(chr, msg))
            if encoded_msg == self.DISCONNECT_MSG:
                # connected = False
                break
            print(f"[{addr}] Request to server: {encoded_msg}")
            response = self.controller.handle_request(encoded_msg)
            response_str = response.get_string_res()
            reply_data = bytearray(response_str, "utf-8")
            print(f"[{addr}] Response from server: {response_str}")
            conn.sendall(reply_data)

        conn.close()

    def run(self):
        self.PORT = int(open("port.info", 'r').read())
        print("[STARTING] Server is starting ...")
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind(self.ADDR)
        server.listen()
        print(f"[LISTENING] Server is listening on {self.IP}:{self.PORT}")

        while True:
            conn, addr = server.accept()
            thread = threading.Thread(target=self.handle_client, args=(conn, addr))
            thread.start()
            print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1} ")


if __name__ == "__main__":
    server = Server()
    server.run()
