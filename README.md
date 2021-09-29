# Simple HTTPServer written for Python3.x

This repository contains code for a multi-threaded http-server written using the standard socket library found in Python.
The only requirement is that you run the code with a Python version ```>=3.0```, as it does not support Python2.x<br>

## Cloning and setup
To download and run the server, do the following:
```
$ git clone git@github.com:willeagren/pyserver
$ cd pyserver
$ sudo chmod +x server.py
$ sudo ./server.py <host_addr> <host_port>
```

I know, it is as simple as that! Simply move the server.py file and src/ directory to the directory containing the files which you want to host.
The directory structure of the server relative to the .html .css and .js files is not important, as long as it is placed **above**, i.e.
```
example_webpage/
├── html/
│   ├── css/
|   |   └── ...
│   ├── js/
|   |   └── ...
│   └── fonts/
|   |   └── ...
|   └── images/
|       └── ...
├── src/
│   └── HTTPServer.py
│   └── SocketBuffer.py
│   └── SocketThread.py
└── server.py
```
The SocketBuffer will recursively search through the directory, from the root location (example_webpage/), so you can place the files just about anywhere and it will still be able to respond with the requested files.

Author: Wilhelm Ågren, wagren@kth.se<br>
License: GNU General Public License v3.0
