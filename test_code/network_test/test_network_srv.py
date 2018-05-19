#!/usr/bin/env python 
# _*_ coding:utf-8 _*_

import sys
import socket

def server():
    msglen = 0
    sockfd = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
    host = socket.gethostname()
    port = 7890
    sockfd.bind((host, port))
    sockfd.listen(5)
    while True:
        clifd, addr = sockfd.accept()
        print('connected host: %s' % str(addr))
        msg = 'welcome to castles'
        msglen += clifd.send(msg.encode('utf-8'))
        if 1024 <= msglen:
             #clifd.close()
            break
        
def main():
    server()

if __name__ == '__main__':
    main()