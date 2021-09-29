import os
import time
import socket
import threading

from .SocketThread import SocketThread


ERROR       = "[!]  ERROR:"
WORKING     = "[*] "
CLOSING     = "[-] "


class HTTPServer:
    """
    !!! definition for class  HTTPserver !!!
    simple http server used for handling simple GET requests. yes, it's simple.
    ,,multi´´-threaded using the threading library and class SocketThread.
    connections implemented using the socket standard library for Python3.8
    the server is set up on a given host IPv4 address and port, and then 
    listens for incoming traffic. if multiple connections are made simultaneously
    multiple SocketThreads will be initialized to respond to requests.
    the server is currently run by executing file server.py in root folder

    public  funcs:
        $ listen()      =>  none
    
    private funcs:
        $ _initialize_socket()                  =>  socket.socket || exit()
        $ _shutdown()                           =>  exit()
        $ _wait4accept()                        =>  (socket.socket, tuple)
        $ _open_client(socket.socket, tuple)    =>  SocketThread
        $ _close_client()                       =>  none

    the initializer for HTTPServer takes two mandatory arguments:
        string host_addr    (host address, IPv4)
        int port            (port to bind socket to)

    valid dict kwargs keywords:
        int recv_size       (number of bytes to read from client request)
        int backlog         (number of clients to buffer)
        int timeout         (number of seconds until client timeouts if no request)
        bool verbose        (enable/disable verbose mode)

    TODO:   debug threading to see if it actually works xD
    """
    def __init__(self, host_addr, port, **kwargs) -> None:
        self.host_addr, self.port, self.threads = host_addr, port, threading.active_count()
        self.recv_size  = kwargs.get("recv_size", 1024)
        self.backlog    = kwargs.get("backlog", 5)
        self.timeout    = kwargs.get("timeout", 30)
        self.verbose    = kwargs.get("verbose", False)
        self.serv_sock = self._initialize_socket()


    def _initialize_socket(self):
        """
        @spec  _initialize_socket(HTTPServer)  =>  socket.socket
        func initializes a socket on given host_addr and port, set 
            socket to listen on AF_INET=IPv4 addresses and SOCK_STREAM=TCP.
            setsockopt needs level to assign option to, SOL_SOCKET is 
            socket level. set it to reuse the address.
            if the socket can't be bound to the provided HOST addr and port,
            then terminate the program. otherwise it returns the socket.socket

        >>>  call:      HTTPServer._initialize_socket()
        >>>  OUTPUT:    socket.socket
        """
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
        """
        @spec  _shutdown(HTTPServer)  =>  exit()
        func disconnects all current client connections and closes the open socket.
            currently only called whenever host/user initiates C-c, KeyboardInterrupt.

        TODO: implement cleaning of tmp files and correct closing of all SocketThreads.

        >>>  call:      HTTPServer._shutdown()
        >>>  OUTPUT:    exit()

        !!! primarily called from func  listen/1, on exception KeyboardInterrupt.
        """
        print(CLOSING+" closing socket ...")
        self.serv_sock.close()
        print(CLOSING+" done! thanks for using HTTPserver")
        exit()


    def _wait4accept(self):
        """
        @spec  _wait4accept(HTTPServer)  =>  (socket.socket, tuple)
        func waits for new connection to server socket and then accepts it.
            the accept() returns a tuple with socket.socket and IPv4 addr, port.
            func returns the tuple pair in order to create new SocketThread.

        >>>  call:      HTTPServer._wait4accept()
        >>>  OUTPUT:    (socket.socket, ('192.168.0.1', 80))

        !!! primarily called from func  listen/1
        """
        clt, addr = self.serv_sock.accept()
        return clt, addr


    def _open_client(self, clt, addr):
        """
        @spec  _open_client(HTTPServer, socket.socket, tuple)  =>  SocketThread
        func increments number of threads for HTTPServer, sets timeout for 
            client connection to host specified int, initializes a new
            SocketThread object with given client socket.socket and addr
            tuple IPv4 and port number. returns the SocketThread

        >>>  call:      HTTPServer._open_client(socket.socket, ('192.168.0.1',15861))
        >>>  OUTPUT:    SocketThread

        !!! primarily called from func  listen/1 when accepting new connection from client
        """
        self.threads += 1
        clt.settimeout(self.timeout)
        sock_t = SocketThread(self.threads, clt, addr, recv_size=self.recv_size, verbose=self.verbose)
        return sock_t


    def _close_client(self):
        """
        @spec  _close_client(HTTPServer)  =>  none
        func simply decrements the number of threads that the HTTPServer is running.
            can't do this from the threads when closing them, so this is run
            after a thread is done and is closing connection.

        >>>  call:      HTTPServer._close_client()
        >>>  OUTPUT:    none

        !!! primarily called from func  listen/1 after closed connection
        """
        self.threads = threading.active_count()
   

    def listen(self):
        """
        @spec  listen(HTTPServer)  =>  none
        func starts listening on the specified port. backlog specifies how many buffered 
            connections the socket is allowed to have. it accepts socket connections
            and spawns new threads with a target job if the spawning of the thread
            was successfull. also monitors KeyboardInterrupt exception which 
            cleans the server dir and closes all opened sockets.

        >>>  call:      HTTPserver.listen()
        >>>  OUTPUT:    none

        !!! primarily called from the main file for the server (../server.py)
        """
        print(WORKING+" listening on opened port ... (backlog={})".format(self.backlog))
        self.serv_sock.listen(self.backlog)
        while True:
            try:
                clt, addr = self._wait4accept()
                sock_t = self._open_client(clt, addr)
                if sock_t.alive:
                    sock_t.start()
                    self._close_client()
            except KeyboardInterrupt:
                print("\n"+ERROR+" got keyboard interrupt. shutting down server ...")
                self._shutdown()

