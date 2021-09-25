#!/bin/python3
from src.server import HTTPServer


BANNER      = """
         __ _________________                          
        / // /_  __/_  __/ _ \___ ___ _____  _____ ____
       / _  / / /   / / / ___(_-</ -_) __/ |/ / -_) __/
      /_//_/ /_/   /_/ /_/  /___/\__/_/  |___/\__/_/   
                                                       
                #!-- by (ulysses@bund) --!#
                          rm -rf
"""

HOST_TMP     = "192.168.0.105"
PORT_TMP     = 80


if __name__ == "__main__":
    #& Run server
    print(BANNER)
    server = HTTPServer(HOST_TMP, PORT_TMP, backlog=1)
    server._listen()
