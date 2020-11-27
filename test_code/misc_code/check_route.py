

#coding:utf-8

import os,sys,time
import telnetlib
import logging
import subprocess
import winsound

class TelnetCli:
    count = 0
    def __init__(self):
        self.ip = "192.168.1.1"
        self.username = "root"
        self.password = "shujujieru_1870_201809"
        self.tc = telnetlib.Telnet()

    def login(self):
        try:
            self.tc.open(self.ip,port=23)
        except:
            logging.warning("%s login fail.", self.ip)
            return False
        
        #self.tc.set_debuglevel(1)
        self.tc.read_until(b'login', timeout=300)
        self.tc.write(self.username.encode('ascii') + b'\n')
        self.tc.read_until(b'Password', timeout=20)
        self.tc.write(self.password.encode('ascii') + b'\n')
        time.sleep(2)

        result = self.tc.read_very_eager().decode('ascii')
        if 'Login incorrect' not in result:
            logging.warning('%s login OK', self.ip)
            return True
        else:
            logging.error('%s login NOK', self.ip)
            return False

    def generate_log(self):
        # create shell script file
        gen_script="cd /tmp;touch collectinfo;chmod +x collectinfo"
        try:
            self.tc.write(gen_script.encode('ascii') + b'\n')
        except:
            return False

        # generate script content
        script_cmd="""
        #!/bin/sh
        ppptid=$(ip rule show  | grep "172." | awk '{print $NF}')
        nastid=$(ip rule show  | grep "192." | grep -v "46" | awk '{print $NF}')

        cd /tmp
        dmesg > defaultrt_console_log
        ip rule show >> defaultrt_console_log
        ip route show table main >> defaultrt_console_log
        ip route show table $ppptid >> defaultrt_console_log
        ip route show table $nastid >> defaultrt_console_log
        suffix=$(date "+%s")
        tar -zcf defaultrt$suffix.tar ppp1.log defaultrt_console_log
        tftp -pl defaultrt$suffix.tar 192.168.1.2
        """

        gen_script=script_cmd + " > collectinfo"
        try:
            self.tc.write(gen_script.encode('ascii') + b'\n')
        except:
            return False

        # exec script
        gen_script="./collectinfo\r\n"
        try:
            self.tc.write(gen_script.encode('ascii') + b'\n')
        except:
            return False

        time.sleep(10)
        self.tc.close()
        return True

    def checkRoute(self):
        cmd_str = "ip route show | grep default"
    
        try:
            self.tc.write(cmd_str.encode('ascii') + b'\n')
        except:
            return False
        
        time.sleep(2)
        recv_content = self.tc.read_very_eager().decode('ascii')
        rule = recv_content.split('\r\n')[1]
        if 14 < len(rule):
            TelnetCli.count = 0
            rule_list = rule.split(' ')
            if 1 < len(rule_list):
                print(time.strftime("%Y-%m-%d %H:%M:%S") + '|default route gateway:' + rule_list[2])
        else:
            print(time.strftime("%Y-%m-%d %H:%M:%S") + '|default route rule LOST,WARNNING!!!')
            winsound.Beep(600,1000)
            TelnetCli.count += 1
            if 1 == TelnetCli.count:
                self.generate_log()

        return True

    def devReboot(self):
        cmd_str = "reboot"
        try:
            self.tc.write(cmd_str.encode('ascii') + b'\n')
        except:
            return False
        

def check_loop():
    start = time.time()
    while True:
        tc = TelnetCli()
        if True == tc.login():
            pass
        else:
            print(time.strftime("%Y-%m-%d %H:%M:%S") + "|login fail and try...")

        tc.checkRoute()
        time.sleep(60) 

        if 180 < time.time() - start:
            start = time.time()
            tc.devReboot()
            time.sleep(300)


if __name__ == "__main__":
    check_loop()



    
