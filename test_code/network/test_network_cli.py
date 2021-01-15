#!/usr/bin/env python
# _*_ coding:utf-8 _*_

import socket
import sys
import time

def client():
    msglen = 0
    sockfd = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
    host = socket.gethostname()
    port = 7890
    sockfd.connect((host, port))
    while True:
        time.sleep(1)
        data = sockfd.recv(1024)
        print(data.decode('utf-8'))
        msglen += len(data)
        if 1024 <= msglen:
            break 
    sockfd.close()    


def main():
    client()

if __name__ == '__main__':
    main()