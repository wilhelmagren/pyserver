import os
import time


ERROR       = "[!]  ERROR:"
WORKING     = "[*] "
CLOSING     = "[-] "


class SocketBuffer:
    def __init__(self, tid, clt, addr, recv_size, **kwargs):
        self.tid, self.clt, self.addr, self.recv_size = tid, clt, addr, recv_size
        self.buff = b""


    def _parse_request(self, req):
        lines = req.split("\n")
        
        (method, fpath, protocol) = lines[0].split(" ")
        print(WORKING+" [{}]  thread={} request: {} {} {}".format(time.asctime(), self.tid, method, fpath, protocol))

        req_ftpe = self._file_type(fpath)
        found_f  = self._find_file(fpath)

        resp_code, resp_msg, f_contents = 404, "Not Found", ""
        resp_contents = open(os.path.join("./html/", "404.html")).read()
        response =  """{} {} {}
                    Content-Type: text/html
                    """
        response = response + "\n\n"

        if found_f:
            resp_code, resp_msg = 200, "OK"
            read_tpe = "r" if req_ftpe == "text" else "rb"
            f_contents = open(found_f, read_tpe).read()
        
        response = response.format(protocol, resp_code, resp_msg)
        if req_ftpe == "image":
            response = response.encode()
        response = response + f_contents
        return response

    
    def _file_type(self, req_file):
        if req_file == "/":
            return "text"

        web_endings     = [".html", ".css", ".js"]
        image_endings   = [".ico", ".jpg", ".jpeg", ".png", ".webp", ".svg"]

        for ending in web_endings:
            if ending in req_file:
                return "text"
        for ending in image_endings:
            if ending in req_file:
                return "image"
        return "text"


    def _find_file(self, req_file):
        """
        @spec  _find_file(SocketBuffer, string)  =>  string
        func takes the requested file from connected client and
            initiates recursive find for file in cwd and respective
            sub directories. if the file is found, the path to it
            is returned as a string. not a file object.

        >>>  call:      SocketBuffer._find_file("/index.html")
        >>>  OUTPUT:    "./html/index.html"

        !!! primarily called from func  _parse_request/2
        """
        curr_dir = os.getcwd()
        
        if req_file == "/":
            return os.path.join(curr_dir, "html/index.html")
        
        if req_file == "/favicon.ico":
            return os.path.join(curr_dir, "favicon.ico")
        
        f_endings = [".html", ".ico", ".png", ".jpg", ".webp"]
        if "." not in req_file:
            req_file += ".html"

        if "/" not in req_file:
            req_file.insert(0, "/")
       
        if "/images/" in req_file:
            req_file = req_file[7:]

        path_to_file = self._find_file_r(req_file[1:], curr_dir)
        return path_to_file


    def _find_file_r(self, req_file, curr_dir):
        """
        @spec  _find_file_r(ClientThread, string, string)  =>  string
        func recursively searches through the sub directories of the current directory
            provided as arg, curr_dir. filters all files containing arbitrary endings,
            needs to be changed since files can have no ending. look up how to verify
            if something is a directory or a file with <os>.
        >>>  call:      ClientThread._find_file_r("index.html", ["css", "html", "src"])
        >>>  OUTPUT:    "html/index.html"
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


    def get_data(self):
        data = self.clt.recv(self.recv_size)
        if not data:
            return ""
        return data.decode()


    def get_bytes(self, n):
        while len(self.buff) < n:
            data = self.clt.recv(self.recv_size)
            if not data:
                data = self.buff
                self.buff = b""
                return data
            self.buff += data
        data, self.buff = self.buff[:n], self.buff[n:]
    

    def put_bytes(self, response):
        self.clt.sendall(response)


    def get_utf8(self):
        data = self.clt.recv(self.recv_size)
        if not data:
            return ""
        self.buff += data
        data, _, self.buff = self.buff.partition(b"\x00")
        return data.decode()


    def put_utf8(self, response):
        self.clt.sendall(response.encode()+b"\x00")
    
    
    def get_parse_send(self):
        """
        returns a response and the filetype [text, image]
        """
        req = self.get_data()
        response = self._parse_request(req)
        if type(response) == str:
            self.put_utf8(response)
        elif type(response) == bytes:
            self.put_bytes(response)
        else:
            print(ERROR+" unknown requested file type. denying request, closing connection ...")


