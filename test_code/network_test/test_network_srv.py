#!/usr/bin/env python
# _*_ coding:utf-8 _*_

import sys
import socket

def client():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
    host = socket.gethostname()
    print(host)
    port = 9999
    s.connect((host, port))

    msg = s.recv(1024)
    
    s.close()
    print(msg.decode('utf-8'))

def server():
    sersock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
    host = socket.gethostname()
    port = 9999
    sersock.bind((host, port))
    sersock.listen(10)

    while True:
        clisock, addr = sersock.accept()
        print('connected addr: %s' % str(addr))
        msg = 'welcome to caltels\r\n'
        clisock.send(msg.encode('utf-8'))
        clisock.close()

def main():
    server()

if __name__ == '__main__':
    main()