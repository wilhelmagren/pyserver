import os
import time
import socket
import threading


ERROR       = "[!]  ERROR:"
WORKING     = "[*] "


class HTTPServer:
    """
    AF_INET         : IPv4 address family
    SOCK_STREAM     : TCP
    """
    def __init__(self, host_addr: str, port: int, **kwargs) -> None:
        self.host_addr, self.port, self.threads = host_addr, port, -1
        self.recv_size  = kwargs.get("recv_size", 1024)
        self.backlog    = kwargs.get("backlog", 5)
        self.timeout    = kwargs.get("timeout", 60)
        self.verbose    = kwargs.get("verbose", False)
        self.serv_sock = self._initialize_socket()

    def _initialize_socket(self):
        serv_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        serv_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            print(WORKING+" binding socket to {}:{}".format(self.host_addr, self.port))
            serv_sock.bind((self.host_addr, self.port))
            return serv_sock
        except:
            print(ERROR+" could not initialize socket binding to {}:{}, terminating...".format(self.host_addr, self.port))
            exit()
    
    def _close_client(self, clt):
        self.threads -= 1
        clt.close()

    def _listen(self):
        """
        Listen for incoming traffic on specified port, accept socket connections and 
        spawn new threads with target job .handle_client given client and address.
        """
        print(WORKING+" listening on opened port ... (backlog={})".format(self.backlog))
        self.serv_sock.listen(self.backlog)  #Backlog=5, number of unaccepted connections the system allows
        while True:
            clt, addr = self.serv_sock.accept()
            print("\n"+WORKING+" got connection, spawning new thread...")
            clt.settimeout(self.timeout)
            self.threads += 1
            thread = threading.Thread(target=self._handle_client, args=(clt, addr, self.threads))
            try:
                thread.start()
            except:
                print(ERROR+" could not spawn thread to deal with client {} at addr {}, continuing".format(clt, addr))
                self.threads -= 1
                continue

    def _handle_client(self, clt, addr, thrd):
        """
        Handle the client, work on implementing this for webpage.
        """
        print(WORKING+" thread={} handling client with addr={}".format(thrd, addr))
        while True:
            try:
                req = clt.recv(self.recv_size)
                if req:
                    response = self._parse_request(req.decode(), thrd)
                    response = "HTTP/1.1 200 OK\nContent-Type: text/html\n\n<h1>Hello World</h1>"
                    clt.sendall(response.encode())
                    print(WORKING+" thread={} response sent".format(thrd))
                    self._close_client(clt)
                    return
                else:
                    print(ERROR+" client disconnected. closing connection on thread={}".format(thrd))
                    self._close_client(clt)
                    return
            except:
                print(WORKING+" thread={} got no data from addr={}".format(thrd, addr))
                self._close_client(clt)
                return

    def _parse_request(self, req, thrd):
        print(WORKING+" got request:{}".format(req)) if self.verbose else print(WORKING+" thread={} parsing request".format(thrd))
        return 1

