

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
            self.tc.open(self.ip, port=23)
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
            logging.info('%s login OK', self.ip)
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

    def check_cwmp(self):
        #check cwmp cmd
        cmd_str = """/bin/ps www |grep cwmp | grep -v '\[' |grep -v grep |/usr/bin/awk '{print $1}'"""
        #kill cwmp
        kill_str = """kill -9 $(/bin/ps www |grep cwmp | grep -v '\[' |grep -v grep |/usr/bin/awk '{print $1}')"""
        #tftp cmd
        tftp_str = "cp -f /tmp/dcycle.log /tmp/dcycle$(date '+%Y%m%d%H%M%S').log;/usr/bin/tftp -pl /tmp/dcycle2021*.log 192.168.1.20;rm -f /tmp/dcycle2021*.log"

        while True:
            self.tc.write(cmd_str.encode('ascii') + b'\n')
            time.sleep(2)
            recv_content = self.tc.read_very_eager().decode('ascii')
            #cwmp not running
            if 0 == len(recv_content):
                self.tc.write(tftp_str.encode('ascii') + b'\n')
                time.sleep(2)
                break
            else:
                self.tc.write(kill_str.encode('ascii') + b'\n')
                time.sleep(300) 

    def check_entry(self, node):
        entrys = ['Entry0','Entry1', 'Entry2']
        tcapi_str = """/userfs/bin/tcapi show WanInfo_"""
        grep_str = """ | grep """

        for entry in entrys:
            conn_str = tcapi_str + entry + grep_str + node
            try:
                self.tc.write(conn_str.encode('ascii') + b'\n')
                time.sleep(1)
                recv_content = self.tc.read_very_eager().decode('ascii')
            except ConnectionAbortedError:
                logging.error('ConnectionAbortedError!!!')
                continue
            except EOFError:
                logging.error('tate EOFError!!!')
                continue
            
            node_lists = recv_content.split('\r\n')
            if len(node_lists) < 3:
                continue
            
            node_value = node_lists[1]
            nodes = node_value.split('=')
            logging.info('%s : %s', entry, node_value)
            if nodes[0] == 'Status':
                if nodes[1] != 'up':
                    return False
            elif nodes[0] == 'SecDNS':
                if len(nodes[1]) < 1:
                    return False
            else:
                return False
        return True

    def check_reboot(self):
        reboot_str = """/sbin/reboot"""
        try:
            self.tc.write(reboot_str.encode('ascii') + b'\n')
        except ConnectionAbortedError:
            logging.error('ConnectionAbortedError!!!')
        except EOFError:
            logging.error('EOFError!!!')

    def check_traffic(self):
        reboot_str = """tcapi get XPON_Common trafficStatus"""
        try:
            self.tc.write(reboot_str.encode('ascii') + b'\n')
            time.sleep(1)
            recv_content = self.tc.read_very_eager().decode('ascii')
        except ConnectionAbortedError:
            logging.error('ConnectionAbortedError!!!')
        except EOFError:
            logging.error('EOFError!!!')
            
        node_lists = recv_content.split('\r\n')
        if len(node_lists) < 3:
            return False
        if node_lists[1] == 'up':
            return True
        return False
            
            
    def check_waninfo(self):
        self.count += 1
        logging.info('check begin(%d)...', self.count)
        correct = True
        while True:
            #check pon traffic
            if not self.check_traffic():
                time.sleep(5)
                continue
            
            #check status
            correct = self.check_entry('Status=')
                
            #check dns
            if True == correct and self.check_entry('SecDNS='):
                self.check_reboot()
                break
            logging.info('waninfo lost!!!')
            time.sleep(5)
        logging.info('check done(%d)...', self.count)
        time.sleep(300)
 
             
if __name__ == "__main__":
    tc = TelnetCli()
    logging.basicConfig(level = logging.DEBUG)
    while True:
        try:
            if True == tc.login():
                pass
            else:
                logging.warning('%s login fail and trying', tc.ip)
                time.sleep(10)
                continue
        except BaseException:
            logging.warning('login exception occurs!!!')
            time.sleep(10)
            
        tc.check_waninfo()



    
