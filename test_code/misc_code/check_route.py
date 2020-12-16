

#coding:utf-8

import os,sys,time
import telnetlib
import logging
import subprocess
import winsound

CHECK_LOOP_TIMEOUT = 60  #seconds
REBOOT_TIMEOUT = 600    #seconds
REBOOT_WAITTIME = 240  #seconds

class TelnetCli:
    count = 0
    lost = 0
    first_login = 0
    def __init__(self):
        self.ip = "192.168.1.1"
        self.username = "root"
        self.password = "shujujieru_1870_201809"
        self.tc = telnetlib.Telnet()

    def save_dmesg(self):
        if 0 == TelnetCli.first_login:
            command='cd /tmp;dmesg -c > defaultrt_console_log'
            try:
                self.tc.write(command.encode('ascii') + b'\n')
            except:
                return False
        else:
            command='cd /tmp;dmesg -c >> defaultrt_console_log'
            try:
                self.tc.write(command.encode('ascii') + b'\n')
            except:
                return False

        TelnetCli.first_login += 1
        return True

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
            self.save_dmesg()
            return True
        else:
            logging.error('%s login NOK', self.ip)
            return False


    def generate_log(self):
        '''
        # create shell script file
        gen_script="cd /tmp;touch collectinfo;chmod +x collectinfo"
        try:
            self.tc.write(gen_script.encode('ascii') + b'\n')
        except:
            return False
        '''
        # generate script content
        """根据自己PC的地址修改tftp命令的目的IP"""
        script_cmd="""
        #!/bin/sh
        ppptid=$(ip rule show  | grep "172." | awk '{print $NF}')
        nastid=$(ip rule show  | grep "192." | grep -v "46" | awk '{print $NF}')

        cd /tmp
        dmesg -c >> defaultrt_console_log
        ip rule show >> defaultrt_console_log
        echo -------------- >> defaultrt_console_log
        ip route show table main >> defaultrt_console_log
        echo -------------- >> defaultrt_console_log
        ip route show table $ppptid >> defaultrt_console_log
        echo -------------- >> defaultrt_console_log
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
        gen_script="/bin/sh ./collectinfo\r\n"
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
                return False
        else:
            print(time.strftime("%Y-%m-%d %H:%M:%S") + '|default route rule LOST,WARNNING!!!')
            winsound.Beep(600,1000)
            winsound.PlaySound("SystemExit", winsound.SND_LOOP)
            winsound.MessageBeep(eval("winsound.MB_ICONEXCLAMATION"))
            TelnetCli.count += 1
            TelnetCli.lost = 1
            if 1 == TelnetCli.count:
                self.generate_log()
                return True


    def devReboot(self):
        cmd_str = "reboot\r\n"
        try:
            self.tc.write(cmd_str.encode('ascii') + b'\n')
        except:
            return False
        

def check_loop():
    start = time.time()
    while True:
        TelnetCli.lost = 0
        tc = TelnetCli()
        if True == tc.login():
            pass
        else:
            print(time.strftime("%Y-%m-%d %H:%M:%S") + "|login fail and try...")

        tc.checkRoute()
        
        # keep device left when error occured
        if (REBOOT_TIMEOUT < (time.time() - start)) and (0 == TelnetCli.lost):
            start = time.time()
            tc.devReboot()
            time.sleep(REBOOT_WAITTIME)
            
        time.sleep(CHECK_LOOP_TIMEOUT)


if __name__ == "__main__":
    check_loop()


