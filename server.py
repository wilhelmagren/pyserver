#!/bin/python3
import sys
from src.HTTPServer import HTTPServer


ERROR       = "[!]  ERROR:"
WORKING     = "[*]  "
CLOSING     = "[-]  "
BANNER      = """
         __ _________________                          
        / // /_  __/_  __/ _ \___ ___ _____  _____ ____
       / _  / / /   / / / ___(_-</ -_) __/ |/ / -_) __/
      /_//_/ /_/   /_/ /_/  /___/\__/_/  |___/\__/_/   
                                                       
                #!-- by (ulysses@bund) --!#
                          rm -rf
"""


if __name__ == "__main__":
    HOST_ADDR = "127.0.0.1"
    HOST_PORT =  80
    try:
        HOST_ADDR = sys.argv[1]
        HOST_PORT = sys.argv[2]
    except:
        print(ERROR+" please specify host address and port. run program like:\n$ sudo ./server.py <host_addr> <host_port>")
        exit()
    
    print(BANNER)  # You got to have a banner!

    server = HTTPServer(str(HOST_ADDR), int(HOST_PORT), backlog=5, recv_size=8192, verbose=True)
    server.listen()

