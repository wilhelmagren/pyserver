#!/bin/python3
import os
import socket
import threading


ERROR       = "[!]  ERROR:"
WORKING     = "[*] "
CLOSING     = "[-] "
HOST_TMP    = "192.168.0.105"
PORT_TMP    =  80
NUM_THREADS =  5


def call_socket(tid):
    request = "GET /index.hml HTTP/1.1\nHost: {}".format(HOST_TMP)
    print(WORKING+" thread={} opening socket and connecting ...".format(tid))
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    addr = (HOST_TMP, PORT_TMP)
    sock.connect(addr)
    sock.send(request.encode())
    response = ""
    while True:
        resp = sock.recv(1024)
        if not resp:
            break
        response += resp.decode()
    print(WORKING+" thread={} got full repsonse. closing ...".format(tid))
    sock.close()


if __name__ == "__main__":
    threads = []
    for t_idx in range(NUM_THREADS):
        new_thread = threading.Thread(target=call_socket, args=(t_idx,))
        threads.append(new_thread)

    for t_idx, t in enumerate(threads):
        print(WORKING+" thread={} starting ...".format(t_idx))
        t.start()

    print(CLOSING+" done! how did it go?")

