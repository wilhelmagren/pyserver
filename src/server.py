import os
import time
import socket


class HTTPServer:
    def __init__(self, HOST, PORT, **kwargs):
        self.hostname, self.port = HOST, PORT

    def run(self):
        print("[*] {}  starting HTTPServer on {}".format(time.asctime(), self.HOST))
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((self.HOST, self.PORT))
        server_socket.listen(1)
        print("[*] {}  listening in port {} ...".format(time.asctime(), self.PORT))


if __name__ == "__main__":
    #& Run server
    server = HTTPServer()
    server.run()
