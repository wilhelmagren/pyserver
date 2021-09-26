import os
import time
import socket

from .client_thread import ClientThread


ERROR       = "[!]  ERROR:"
WORKING     = "[*] "
CLOSING     = "[-] "


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
    
    
    def _shutdown(self):
        print(CLOSING+" closing socket ...")
        self.serv_sock.close()
        print(CLOSING+" done! thanks for using HTTPserver")
        exit()


    def _wait4accept(self):
        clt, addr = self.serv_sock.accept()
        print()
        print(WORKING+" got connection, initializing new thread ...".format(addr))
        return clt, addr


    def _open_client(self, clt, addr):
        self.threads += 1
        clt.settimeout(self.timeout)
        clt_thread = ClientThread(self.threads, clt, addr, recv_size=self.recv_size)
        return clt_thread


    def _close_client(self):
        self.threads -= 1
   

    def listen(self):
        """
        Listen for incoming traffic on specified port, accept socket connections and 
        spawn new threads with target job .handle_client given client and address.
        """
        print(WORKING+" listening on opened port ... (backlog={})".format(self.backlog))
        self.serv_sock.listen(self.backlog)
        while True:
            try:
                clt, addr = self._wait4accept()
                clt_thread = self._open_client(clt, addr)
                if clt_thread.alive:
                    clt_thread.start()
                    self._close_client()
            except KeyboardInterrupt:
                print("\n"+ERROR+" got keyboard interrupt. shutting down server ...")
                self._shutdown()

