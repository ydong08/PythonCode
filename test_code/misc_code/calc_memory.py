

#coding:utf-8

import os,sys,time
import telnetlib
import logging
import subprocess

class TelnetCli:
    def __init__(self):
        self.ip = "192.168.1.1"
        self.username = "root"
        self.password = "shujujieru_1870_201809"
        self.count = 0
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

    def get_int_result_cmd(self, cmd):
        self.tc.write(cmd.encode('ascii') + b'\n')
        time.sleep(1)
        result = self.tc.read_very_eager().decode('ascii').split('\r\n')
        #print(result)
        if True == result[1].isdecimal():
            return int(result[1])
        else:
            return 0

    def calcMemory(self):
        vsz_origin = {}
        rss_origin = {}

        try:
            fd = open("result_memory", "w")
        except:
            logging.error("open result fial.")
            return False

        cmd_str = """/bin/ps www | grep -v '\[' | /usr/bin/awk '{if(NR>1)print $1}'"""
        self.tc.write(cmd_str.encode('ascii') + b'\n')
        time.sleep(2)
        recv_content = self.tc.read_very_eager().decode('ascii')
        pidlist = recv_content.split('\r\n')
        pidlist[0] = '0'
        pidlist.remove('# ')

        while True:
            for pid in pidlist:
                if 0 == len(pid) or 0 == int(pid):
                    continue

                status_file = "/proc/" + str(pid) + "/status"
                get_vsz_cmd = "/bin/cat " + status_file + "| grep VmSize | awk '{print $2}'"
                get_rss_cmd = "/bin/cat " + status_file + "| grep VmRSS | awk '{print $2}'"
                numv = self.get_int_result_cmd(get_vsz_cmd)
                nums = self.get_int_result_cmd(get_vsz_cmd)
                if 0 == numv or 0 == nums:
                    continue

                if 0 == self.count:
                    vsz_origin[pid] = numv
                    rss_origin[pid] = nums
                    print('numv:' + str(numv) + ', nums:' + str(nums))
                    
                else:
                    numv = numv - vsz_origin[pid]
                    nums = nums - rss_origin[pid]
                    if 1024 < numv or 1024 < nums:
                        line = "{} {} {}\n".format(pid, numv, nums)
                        fd.write(line)
                        fd.fflush()
                        print('numv_diff:' + str(numv) + ', nums_diff:' + str(nums))
                    time.sleep(600)

            self.count = 1


if __name__ == "__main__":
    tc = TelnetCli()
    if True == tc.login():
        pass
    else:
        logging.warning('%s login fail and exit', tc.ip)
        sys.exit()

    tc.calcMemory()



    
