import os
import time
import threading


ERROR       = "[!]  ERROR:"
WORKING     = "[*] "
CLOSING     = "[-] "


class ClientThread:
    def __init__(self, tid, clt, addr, **kwargs):
        self.tid, self.clt, self.addr = tid, clt, addr
        self.recv_size      = kwargs.get("recv_size", 1024)
        self.thread = self._spawn_thread()
        self.alive = False if not self.thread else True


    def _spawn_thread(self):
        """
        @spec  _spawn_thread(ClientThread)  =>  threading.Thread || none
        func tries to spawn a new thread with target function handle_client/1
            returns the created thread as an attribute to the ClientThread if 
            successful, otherwise return None and set alive attribute to False

        >>>  self._spawn_thread()
        >>>  threading.Thread if successfull else None

        !!! primarily called from func  self.__init__/4+
        """
        try:
            thread = threading.Thread(target=self.handle_client)
            print(WORKING+" thread={} assigned to {}".format(self.tid, self.addr))
            return thread
        except:
            print(ERROR+" could not spawn thread for client at addr={}, continuing ...".format(self.addr))
        return None

    def start(self):
        """
        @spec  start(ClientThread)  =>  none
        func starts the target function bound to ClientThread thread
            see threading library for more information on how threads
            are initialized, started, and terminated

        >>>  self.start()
        >>>  none

        !!! primarily called from func  HTTPServer.listen/1
        """
        self.thread.start()


    def close(self):
        """
        @spec  close(ClientThread)  =>  none
        func closes the client connection assigned to object
            attribtute self.clt. see socket library for details.

        >>>  self.close()
        >>>  none

        !!! primarily called from func  handle_client/1
        """
        self.clt.close()


    def handle_client(self):
        """
        @spec  handle_client(ClientThread)  =>  none
        func called as target function for thread attribute on object
            only executed when outside server calls func start/1, which
            according to threading library starts the execution of the target
            function bound to thread.

        >>>  thread = threading.Thread(target=handle_client)
        >>>  thread.start()
        >>>  none

        !!! bound as target function for threads, indirectly called/executed
                from func  start/1 in HTTPserver.listen/1
        """
        print(WORKING+" thread={} handling client ...".format(self.tid))
        request = self.clt.recv(self.recv_size)
        if request:
            response = self._parse_request(request.decode())
            self.clt.sendall(response.encode())
            print(WORKING+" thread={} response sent".format(self.tid))
        else:
            print(ERROR+" no request from client. closing connection and thread={}".format(self.tid))
        self.close()

    
    def _find_file(self, req_file):
        """
        @spec  _find_file(ClientThread, string)  =>  string
        func takes the requested file from connected client and
            initiates recursive find for file in cwd and respective
            sub directories. if the file is found, the path to it
            is returned as a string. not a file object.

        >>>  self._find_file("index.html")
        >>>  $PATH/html/index.html

        !!! primarily called from func  _parse_request/2
        """
        curr_dir = os.getcwd()
        if req_file == "/":
            return os.path.join(curr_dir, "html/index.html")
        
        if ".html" not in req_file:
            req_file += ".html"
        
        path_to_file = self._find_file_r(req_file[1:], curr_dir)
        return path_to_file
 
    
    def _find_file_r(self, req_file, curr_dir):
        """
        @spec  _find_file_r(ClientThread, string, string)  =>  string
        func recursively searches through the sub directories of the current directory
            provided as arg, curr_dir. filters all files containing arbitrary endings,
            needs to be changed since files can have no ending. look up how to verify
            if something is a directory or a file with <os>.

        >>>  self._find_file_r("index.html", ["css", "html", "src"])
        >>>  $PATH/html/index.html

        TODO: change the list comprehension filter!!!
        !!! primarily called from func  _find_file/2
        """
        subdirs = list(filter(lambda x: ("." not in x), os.listdir(curr_dir)))
        if req_file in os.listdir(curr_dir):
            return os.path.join(curr_dir, req_file)

        if not subdirs:
            return ""

        s = ""
        for subdir in subdirs:
            s += self._find_file_r(req_file, os.path.join(curr_dir, subdir))
        return s


    def _parse_request(self, request):
        """
        @spec  _parse_request(ClientThread, string)  =>  string
        func takes a client request as a string, parses the method and 
            requested file and returns a formatted HTTP response based
            on result of _find_file/2. currently only supports two
            types of response codes: (200, 404) and always returns
            ,,Content-Type: text/html´´ which may be changed.

        >>>  self._parse_request("GET /index HTTP/1.1\n...")
        >>>  "HTTP/1.1 200 OK\nContent-Type: text/html\n\n<body>"

        TODO: change response code possibilities and Content-Type
        !!! primarily called from func  handle_client/1
        """
        lines = request.split("\n")
        (method, filepath, protocol) = lines[0].split(" ")
        found_file = self._find_file(filepath)
        response_code, response_code_msg = 404, "Not Found"
        response_contents = open(os.path.join("./html/", "404.html")).read() 

        if found_file:
            response_code, response_code_msg = 200, "OK"
            response_contents = open(found_file).read()

        response =   """{} {} {}
                        Content-Type: text/html

                        {}""".format(protocol, response_code, response_code_msg, response_contents)
        return response

