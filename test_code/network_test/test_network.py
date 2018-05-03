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



def server():
    pass

def main():
    client()

if __name__ == '__main__':
    main()