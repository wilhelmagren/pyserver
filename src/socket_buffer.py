import os


ERROR       = "[!]  ERROR:"
WORKING     = "[*] "
CLOSING     = "[-] "


class SocketBuffer:
    def __init__(self, tid, clt, addr, recv_size, **kwargs):
        self.tid, self.clt, self.addr, self.recv_size = tid, clt, addr, recv_size
        self.buff = b""
    

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


