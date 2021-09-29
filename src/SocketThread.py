import os
import time
import socket
import threading

from .SocketBuffer import SocketBuffer


ERROR       = "[!]  ERROR:"
WORKING     = "[*] "
CLOSING     = "[-] "


class SocketThread:
    """
    !!! definition for class  SocketThread !!!
    used heavily in HTTPServer for serving new client connections.
    using threading library to spawn independent Threads based on each
    new client request. threads are indexed from [0-numThreads] in 
    HTTPServer and if the tid (thread id) attr would be negative in the
    SocketThread something has gone wrong in the HTTPServer.

    public  funcs:
        $  start()                  =>  none
        $  close()                  =>  none
        $  handle_client()          =>  none

    private funcs:
        $  _spawn_thread()          =>  threading.Thread || none
        $  _parse_request(string)   =>  string
        $  _find_file(string)       =>  string
        $  _find_file_r(string)     =>  string
    
    the initializer for SocketThread takes three mandatory arguments:
        int tid         (thread id, given by HTTPServer creating the SocketThread)
        socket clt      (client socket, assigned by socket library when connecting)
        tuple addr      (client address, tuple of (string, string)=(IPv4 addr, port))
    
    valid dict kwargs keywords:
        int recv_size   (number of bytes to read from client request)
        bool verbose    (enable/disable verbose mode)

    TODO:   implement new class ,,RequestObj´´ based on client request, in order to
            parse request and build response separately, as this is not specifically
            relevant to the SocketThread object.
    """
    def __init__(self, tid, clt, addr, **kwargs):
        self.tid, self.clt, self.addr = tid, clt, addr
        self.recv_size      = kwargs.get("recv_size", 1024)
        self.verbose        = kwargs.get("verbose", False)
        self.thread         = self._spawn_thread()
        self.alive          = False if not self.thread else True


    def _spawn_thread(self):
        """
        @spec  _spawn_thread(SocketThread)  =>  threading.Thread || none
        func tries to spawn a new thread with target function handle_client/1
            returns the created thread as an attribute to the SocketThread if 
            successful, otherwise return None and set alive attribute to False

        >>>  call:      SocketThread._spawn_thread()
        >>>  OUTPUT:    threading.Thread || none

        !!! primarily called from func  self.__init__/4+
        """
        try:
            thread = threading.Thread(target=self.handle_client)
            print("\n"+WORKING+" [{}]  thread={} assigned to {}".format(time.asctime(), self.tid, self.addr))
            return thread
        except:
            print(ERROR+" could not spawn thread for client at addr={}, continuing ...".format(self.addr))
        return None


    def start(self):
        """
        @spec  start(SocketThread)  =>  none
        func starts the target function bound to SocketThread thread
            see threading library for more information on how threads
            are initialized, started, and terminated

        >>>  call:      SocketThread.start()
        >>>  OUTPUT:    none

        !!! primarily called from func  HTTPServer.listen/1
        """
        self.thread.start()


    def close(self):
        """
        @spec  close(SocketThread)  =>  none
        func closes the client connection assigned to object
            attribtute self.clt. see socket library for details.

        >>>  call:      SocketThread.close()
        >>>  OUTPUT:    none

        !!! primarily called from func  handle_client/1
        """
        print(WORKING+" [{}]  thread={} response sent, closing ...".format(time.asctime(), self.tid))
        self.clt.close()


    def handle_client(self):
        """
        @spec  handle_client(SocketThread)  =>  none
        func called as target function for thread attribute on object
            only executed when outside server calls func start/1, which
            according to threading library starts the execution of the target
            function bound to thread.

        >>>  call:      thread = threading.Thread(target=handle_client)
        >>>  call:      thread.start()
        >>>  OUTPUT:    none

        !!! bound as target function for threads, indirectly called/executed
                from func  start/1 in HTTPserver.listen/1
        """
        try:
           client_buffer = SocketBuffer(self.tid, self.clt, self.addr, self.recv_size)
           client_buffer.get_parse_send()
        except socket.timeout as e:
            print(ERROR+" [{}]  thread={} request timed out: {}".format(time.asctime(), e))
        self.close()


def _parse_request(self, request):
        """
        @spec  _parse_request(SocketThread, string)  =>  string
        func takes a client request as a string, parses the method and 
            requested file and returns a formatted HTTP response based
            on result of _find_file/2. currently only supports two
            types of response codes: (200, 404) and always returns
            ,,Content-Type: text/html´´ which may be changed.

        >>>  call:      SocketThread._parse_request("GET /index HTTP/1.1\n...")
        >>>  OUTPUT:    "HTTP/1.1 200 OK\nContent-Type: text/html\n\n<body>"

        TODO: change response code possibilities and Content-Type
        !!! primarily called from func  handle_client/1
        """
        lines = request.split("\n")
        (method, filepath, protocol) = lines[0].split(" ")
        print(WORKING+" [{}]  thread={} request: {} {} {}".format(time.asctime(), self.tid, method, filepath, protocol))

        req_file_type = self._file_type(filepath)
        found_file = self._find_file(filepath)
        
        response_code, response_code_msg = 404, "Not Found"
        response_contents = open(os.path.join("./html/", "404.html")).read() 
        response =      """{} {} {}
                           Content-Type: text/html
                        """

        if found_file:
            response_code, response_code_msg = 200, "OK"
            if req_file_type == "image":
                response = response.format(protocol, response_code, response_code_msg)
                response += "\n\n"
                response = response.encode()
                file_contents = open(found_file, "rb").read()
                return response+file_contents, req_file_type
            response_contents = open(found_file, "r").read()


        response = response.format(protocol, response_code, response_code_msg) + "\n\n{}".format(response_contents)
        return response, req_file_type

