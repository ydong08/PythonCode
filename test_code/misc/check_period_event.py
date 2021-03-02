#coding:utf-8

import os,sys,time
import telnetlib
import logging
import subprocess

CHECK_LOOP_TIMEOUT = 120  #seconds

class TelnetCli:
    def __init__(self):
        self.ip = "192.168.1.1"
        self.username = "root"
        self.password = "shujujieru_1870_201809"
        self.tc = telnetlib.Telnet()


    def login(self):
        logging.basicConfig(level=logging.INFO)
        try:
            self.tc.open(self.ip,port=23)
        except:
            logging.info("%s login fail.", self.ip)
            return False
        
        #self.tc.set_debuglevel(1)
        self.tc.read_until(b'login', timeout=300)
        self.tc.write(self.username.encode('ascii') + b'\n')
        self.tc.read_until(b'Password', timeout=20)
        self.tc.write(self.password.encode('ascii') + b'\n')
        time.sleep(2)

        result = self.tc.read_very_eager().decode('ascii')
        if 'Login incorrect' not in result:
            logging.info('%s login OK', self.ip)
            return True
        else:
            logging.error('%s login NOK', self.ip)
            return False

    def check_route(self):
        # check script
        script_cmd = "/bin/ip route show"
        try:
            self.tc.write(script_cmd.encode('ascii') + b'\n')
        except:
            return False
        
        recv_content = self.tc.read_very_eager().decode('ascii')
        print('recv_content: ' + recv_content)
        file_name = recv_content.split('\r\n')[0]
        print('route: ' + file_name)

        time.sleep(10)
        self.tc.close()
        return True

def check_loop():
    start = time.time()
    tc = TelnetCli()
    while True:
        tc.login()
        print(time.strftime("%Y-%m-%d %H:%M:%S") + "|try to login...")

        if False == tc.check_route():
            logging.info('check route fail')    
        time.sleep(CHECK_LOOP_TIMEOUT)


if __name__ == "__main__":
    check_loop()


