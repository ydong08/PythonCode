#! /usr/bin/env python3
# _*_ coding:utf-8 _*_

import re
import os
import time
import operator
import serial
import json
import serial.tools.list_ports
#from serial.serialutil import *

"""
operate on windows COM 
"""


def test_com():
    """test windows COM recv and send data"""
    port = []
    plist = list(serial.tools.list_ports.comports())
    for p in plist:
        pcom = list(p)
        device = pcom[0]
        name = pcom[1]
        info = pcom[2]
        print('serial_device: ' + device)
        print('serial_name: ' + name)
        print('serial_info: ' + info)
        if re.search(r'USB-to-Serial', name) is not None:
            port.append(device)
            print(port)

    if len(port) <= 0:
        print("not find windows serial port")
        return False

    loop_num = 100
    if 1 == len(port):
        serial_fd = serial.Serial(port[0], 9600, 8, 'N', 1, 10)
        if serial_fd.is_open:
            print('serial already open OK')
            while loop_num > 0:
                serial_fd.write("send".encode('utf-8'))
                time.sleep(1)
                data = serial_fd.read(7)
                print(data)
                loop_num -= 1
        else:
            print("COM open NOK")

global_msg_type = {'set_config':0xE1,
                                'get_config':0xE2,
                                'set_capk': 0xE3,
                                'get_capk': 0xE4,
                                'del_capk': 0xE5,
                                'get_poll_mode': 0xE6,
                                'reset': 0xE7,
                                'get_serial_num': 0xE8,
                                'get_fw_version': 0xE9,
                                'get_payment_version': 0xEA,
                                'get_vas_version': 0xEB,
                                'start_transaction': 0xEC,
                                'get_trans_status': 0xED,
                                'get_trans_result': 0xEE,
                                'cancel_transaction': 0xEF,
                                'get_trans_log': 0xF0,
                                'clear_trans_log': 0xF1,
                                'close': 0xF2
                   }
class RS232(object):
    """
    RS232 class supply operation on COM
    """
    def __init__(self, devName):
        """init COM some parameter"""
        self.instance = None
        self.port = devName
        self.baud_rate = 9600
        self.byte_size = 8
        self.parity = 'N'
        self.stop_bits = 1
        self.serial_timeout = 10
        self.recv_timeout = 5
        self.com_open = False
        self.__msg_len = 4096 - 12   #after adding msg header and msg info, finally, not exceed 255bytes

        port_list = list(serial.tools.list_ports.comports(True))
        port = []
        # loop all com in system
        for p in port_list:
            pcom = list(p)
            device = pcom[0]
            name = pcom[1]
            if re.search(r'USB-to-Serial', name) is not None:
                port.append(device)
        # if only one serial com, set this default, otherwise, set devName
        if 1 == len(port):
            self.port = port[0]
            try:
                self.instance = serial.Serial(self.port, self.baud_rate,
                                                    self.byte_size, self.parity, self.stop_bits, self.serial_timeout)
            except SerialException as e:
                print('exception occur: %s' % e)
            else:
                if self.instance is not None:
                    if self.instance.is_open:
                        self.com_open = True
                        print('create and open COM on ' + self.port)
        else:
            print("assigned port NOT matched in system")

    def __calc_lrc(self, content):
        lrc_value = 0
        for i in content:
            lrc_value ^= i
        return lrc_value

    def __check_lrc(self, content):
        lrc_value = 0
        for i in content[:-1]:
            lrc_value ^= i
        if lrc_value == content[-1]:
            return True
        else:
            return False

    def __check_msg(self, content):
        """ ensure the content is entire POS command message"""
        if content is None:
            return False
        if operator.lt(len(content), 13):
            return False
        msg_len = content[4:5]*256 + content[5:6]
        if msg_len == len(content[6:-2]):
            data_len = content[11:12]*256 + content[12:13]
            if data_len == len(content[13:-2]):
                return __check_lrc(content[1:])
        return False

    def __get_data(self, content):
        data = content[13:-2]
        return data

    def __create_cmd(self, msg_type, content):
        """ construct POS cmd msg"""
        cmd = bytearray()
        content_len = 0

        cmd.append(0x02)  #STX
        # Message Header
        cmd.append(0x00)    #DID, Destination ID
        cmd.append(0x00)    #SID, SourceID
        cmd.append(0x00)   #MTI, Message Type Indicator
        if content is not None:
            content_len = len(content) + 6  # add ETX & LRC
        else:
            content_len = 6  # add ETX & LRC
        msg_len = int(content_len//256)
        cmd.extend(msg_len.to_bytes(1, byteorder='big'))   #MSB Len
        msg_len = int(content_len % 256)
        cmd.extend(msg_len.to_bytes(1, byteorder='big'))   #LSB Len

        # Message Info
        cmd.append(0x01)  # Type, 01-command, 02-response
        cmd.append(msg_type)  # ID
        cmd.append(0x00)  # P1
        cmd.append(0x00)  # P2
        if content is not None:
            content_len = len(content)
        else:
            content_len = 0  # add ETX & LRC
        msg_len = int(content_len // 256)
        cmd.extend(msg_len.to_bytes(1, byteorder='big'))  # MSB Len
        msg_len = int(content_len % 256)
        cmd.extend(msg_len.to_bytes(1, byteorder='big'))  # LSB Len
        if content is not None:
            cmd.extend(content)
        cmd.append(0x03)   # ETX
        msg_len = int(self.__calc_lrc(cmd[1:]))
        cmd.extend(msg_len.to_bytes(1, byteorder='big'))
        print(cmd)
        return cmd

    def __send_data(self, msg_type, content):
        """ send request command message """
        if self.instance is None:
            return False
        send_data = self.__create_cmd(msg_type, content)
        left_len = len(send_data)
        index = 0
        max_send_len = 0
        while 0 < left_len:
            # send data
            if self.__msg_len < left_len:
                max_send_len = self.__msg_len
            else:
                max_send_len = left_len
            try:
                send_len = self.instance.write(send_data[index:index+max_send_len])
            except TypeError as e:
                print(e)
                break
            else:
                index += send_len
                left_len -= send_len

        # check send result
        if 0 == left_len:
            return True
        else:
            return False

    def __recv_data(self, timeout):
        """ receive com message from terminal """
        data = bytearray()
        if self.instance is None:
            return bytes()
        since = time.time()
        while 0 < self.instance.inWaiting():
            data.extend(self.instance.read())
            if operator.gt(timeout, 0):
                    if (0 == len(data) and (time.time() < since + timeout)):
                        break
        return bytes(data)

    def __check_recv_response(self):
        response_data = bytearray()
        data = self.__recv_data(self.recv_timeout)
        if operator.eq(len(data), 0):
            return bytes()
        if self.__check_msg(data):
                response_data.extend(self.__get_data(data))  # error code
                if operator.le(len(response_data), 2):
                    print("recv msg Invalid")
                    return bytes()
                else:
                    print('recv msg OK')
                    return bytes(response_data)
        else:
            print("recv msg Invalid")
            return bytes()

    def __clear_cache(self):
        if self.instance is not None:
            self.instance.flushInput()
            self.instance.flushOutput()

    def setConfig(self, reader_config_object):
        """ set static reader configuration """
        reader_config = bytes(json.dumps(reader_config_object), "utf-8")
        self.__clear_cache()
        if self.__send_data(global_msg_type['set_config'], reader_config):
            print('send request msg[%d] OK' % len(reader_config))
        else:
            print('send request msg NOK, stop')

    def getConfig(self):
        """ get current config values """
        reader_config = {}
        self.__clear_cache()
        if self.__send_data(global_msg_type['get_config'], None):
            data =  self.__check_recv_response()
            if operator.gt(len(data), 0):
                reader_config = json.loads(self.__get_data(data))
        return reader_config

    #@property
    def getCAPK(self):
        """  CAPK info """
        capk_tuple = ()
        self.__clear_cache()
        if self.__send_data(global_msg_type['get_capk'], None):
            data =  self.__check_recv_response()
            if operator.gt(len(data), 0):
                capk_config = json.loads(self.__get_data(data))
                if isinstance(capk_config, dict):
                    for x in range(len(capk_config)):
                        if isinstance(x, dict):
                            tmp_tuple = tuple(x)
                            capk_tuple += tmp_tuple
        return capk_tuple


    def setCAPK(self, CAPK_object):
        """ set CAPK """
        capk_config = bytes(json.dumps(CAPK_object), "utf-8")
        self.__clear_cache()
        if self.__send_data(global_msg_type['set_config'], capk_config):
            print('send request msg[%d] OK' % len(capk_config))
        else:
            print('send request msg NOK, stop')

    def deleteCAPK(self, CAPK_object):
        """ delete CAPK """
        capk_config = bytes(json.dumps(CAPK_object), "utf-8")
        self.__clear_cache()
        if self.__send_data(global_msg_type['del_capk'], capk_config):
            print('send request msg[%d] OK' % len(capk_config))
        else:
            print('send request msg NOK, stop')

    def getPollingModes(self):
        """ get supported polling modes """
        polling_mode = bytearray()
        self.__clear_cache()
        if self.__send_data(global_msg_type['get_poll_mode'], None):
            # recv response
            data =  self.__check_recv_response()
            if operator.gt(len(data), 0):
                polling_mode.extend(self.__get_data(data))
        return  polling_mode.decode('utf-8')
            
    def reset(self):
        """ reset or reboot terminal """
        self.__clear_cache()
        if self.__send_data(global_msg_type['reset'], None):
            # recv response
            data =  self.__check_recv_response()
            if operator.gt(len(data), 0):
                return True
            else:
                print("recv msg Invalid")
                return False
        else:
            print('send request msg NOK, stop')
            return False

    def getSerialNumber(self):
        """ get terminal serial number """
        serial_number = bytearray()
        self.__clear_cache()
        if self.__send_data(global_msg_type['get_serial_num'], None):
            # recv response
            data =  self.__check_recv_response()
            if operator.gt(len(data), 0):
                serial_number.extend(self.__get_data(data))
            else:
                print("recv msg Invalid")
        else:
            print('send request msg NOK, stop')
            return serial_number.decode('utf-8')

    def getFWVersion(self):
        """ FW version installed on terminal """
        fw_version = bytearray()
        self.__clear_cache()
        if self.__send_data(global_msg_type['get_fw_version'], None):
            # recv response
            data =  self.__check_recv_response()
            if operator.gt(len(data), 0):
                fw_version.extend(self.__get_data(data))
            else:
                print("recv msg Invalid")
        else:
            print('send request msg NOK, stop')
        return fw_version.decode('utf-8')

    def getPaymentAppletVersion(self):
        """ return payment applet version installed on reader """
        payment_version = bytearray()
        self.__clear_cache()
        if self.__send_data(global_msg_type['get_payment_version'], None):
            # recv response
            data =  self.__check_recv_response()
            if operator.gt(len(data), 0):
                payment_version.extend(self.__get_data(data))
            else:
                print("recv msg Invalid")
        else:
            print('send request msg NOK, stop')
        return payment_version.decode('utf-8')

    def getVASAppletVersion(self):
        """ return VAS applet version installed on reader """
        vas_version = bytearray()
        self.__clear_cache()
        if self.__send_data(global_msg_type['get_vas_version'], None):
            # recv response
            data =  self.__check_recv_response()
            if operator.gt(len(data), 0):
                vas_version.extend(self.__get_data(data))
            else:
                print("recv msg Invalid")
        else:
            print('send request msg NOK, stop')
        return vas_version.decode('utf-8')

    def startTransaction(self, transaction_start_object):
        """ put terminal in vas or payment mode """
        trans_config = bytes(json.dumps(transaction_start_object), "utf-8")
        self.__clear_cache()
        if self.__send_data(global_msg_type['start_transaction'], trans_config):
            print('send request msg[%d] OK' % len(trans_config))
        else:
            print('send request msg NOK, stop')

    def getTransactionStatus(self):
        """ get transaction status inprogress, complete, or errorcode """
        trans_status = {}
        self.__clear_cache()
        if self.__send_data(global_msg_type['get_trans_status'], None):
            data =  self.__check_recv_response()
            if operator.gt(len(data), 0):
                trans_status = json.loads(self.__get_data(data))
            else:
                print("recv msg Invalid")
        else:
            print('send request msg NOK, stop')
        return trans_status

    def getTransactionResult(self):
        """ get transaction status which consist of vas or payment status """
        trans_result = {}
        self.__clear_cache()
        if self.__send_data(global_msg_type['get_trans_result'], None):
            data =  self.__check_recv_response()
            if operator.gt(len(data), 0):
                trans_result = json.loads(self.__get_data(data))
            else:
                print("recv msg Invalid")
        else:
            print('send request msg NOK, stop')
        return trans_result

    def cancelTransaction(self):
        """ cancel current transaction or vas mode and return to idle mode """
        if self.__send_data(global_msg_type['cancel_transaction'], None):
            # recv response
            data =  self.__check_recv_response()
            if operator.gt(len(data), 0):
                return True
            else:
                return False
        else:
            print('send request msg NOK, stop')
            return False

    def getTransactionLog(self):
        """ return logObject which consist of a tuple of byte strings for each apdu
         logged duringvas or/ and payment transaction """
        data = bytearray()
        tmp_data = bytearray()
        trans_log = {}
        trans_log_flag = 0
        self.__clear_cache()
        if self.__send_data(global_msg_type['get_trans_log'], None):
            since = time.time()
            while True:
                if 0 < self.instance.inWaiting():
                    data.extend(self.instance.read())
                if operator.ge(len(data), 3):
                    if operator.eq(data[-3], 0xFF):
                        break
                if operator.gt(time.time() - since, 3):
                    if operator.eq(len(data), 0):   #
                        break
                continue
        if self.__check_msg(data):
            tmp_data = self.__get_data(data)
            if operator.gt(len(tmp_data, 1)):   #error code 
                trans_log = {tmp_data[0:-1], tmp_data[-1:]}
        return trans_log

    def clearTransactionLog(self):
        """ close log file for next logging session """
        if self.__send_data(global_msg_type['clear_trans_log'], None):
            # recv response
            data =  self.__check_recv_response()
            if operator.gt(len(data), 0):
                return True
            else:
                return False
        else:
            print('send request msg NOK, stop')
            return False

    def close(self):
        """ close COM connection """
        self.__clear_cache()
        if self.__send_data(global_msg_type['close'], None):
            # recv response
            data =  self.__check_recv_response()
            if operator.gt(len(data), 0):
                if self.com_open:
                    self.instance.close()
                    self.com_open = False
                    print('close connection on COM ' + self.port)
                else:
                    print('connection on COM already closed')
                return True
            else:
                return False
        else:
            print('send request msg NOK, stop')
            return False


 """    
reader_conﬁg_object
{
    "RestoreDefault":h,    
    
    "TransactionLogging":boolean,   
    "TransactionLogSize":h,   
    "TransCurrencyCode":h,   
    "TransCurrencyExponent":h, 
    "TransType":h,   
    
    "AmountAuthorized":h,  
    "AmountOther":h,   
    "TerminalCountryCode":h,   
    "TerminalFloorLimit":h,   
    "TerminalCapabilities":h,   
    "TerminalType":h,   
    "AdditionalTermCapabilities":h,   
    "TerminalCTLSFloorLimit":h, 
    "VisaTTQ":h,   
    "Timeout":time value in ms, 
     
    "mChipMobileSupport":h,   
    "ExpressPayTerminalCapabilities":h, 
    "TerminalCTLSTransLimit":h, 
    "CVMRequiredLimit":h,   
    "TerminalActionCodeOnline":h,   
    "TerminalActionCodeDefault":h,   
    "TerminalActionCodeDenial":h,   
    "pollingMode":h,   
    "pollingTechnology":h,   
    …
    “VAS”: {
    'Merchants' : [
    {
        "merchantID" : string
        "url" : string
        "ﬁlter" : byte string
    },
    …
    ]
    }
}

transaction_start_object 
{
"VASTerminalMode":h,   
"ProtocolMode":h,   
"AmountAuthorized":h,   
"Timeout":time value in ms   
"TransDate":h,    
"TransTime":time value in HHMMSS, 
"TransType":h,   
"TransCurrencyCode":h,  
"TerminalCountryCode":h,   
"AccountType":int,   
"AmountOther":h,    
}

vas_result_object 
{
"token" : h
"data' : h
"merchantID" : string
"result code" : int
}

CAPK_object
{
    "RID":h,
    "CAPKIndex":h,
    "CAHashAlgoIndicator":h,
    "CAPKAlgoIndicator":h,
    "CAPKModulus":h,
    "CAPKExponent":h,
    "CAPKCheckSum":h,
}

transaction_result_object 
{
    "VASResults" : [
    (one for each VAS request in transaction)
    
    vas_result_object_1,
    vas_result_object_2,
    …
    vas_result_object_n
    ]
    "PaymentResult" : {
    "rawdata" : h,
    "track 1": h,
    "track 2": h,
    … some basic values
    }
}

transaction_status_object    
{
    transactionStatus:h,   
VAS and Payment specs
}

logObject 
{
    getLog:string,   
    clearLog:boolean,    
}

server_response_object 
{
    "Online Authorization/Results":string,
}

"""
def test_interface():
    #test data
    reader_config_object = {
    "RestoreResult": 12345678,
    "TransactionLogging": True,
    "TransactionLogSize": 1024,
    "VAS": {
        'Merchant': [{
            'merchantID': "D48EF64464F332DB2E97CD7DEDEE17E82E92086B23027F4FE777A244BE536F16",
            'url': "https://test.pass.mcr.com",
            'filter': "5682"
        },
        {
            'merchantID': "3F22543BAF0AC5E4ABFC25681A6EBF6EDF5AC196746C55F4D4370819FFF921C3",
            'url': "",
            'filter': ""
        }]
        }
    }

    CAPK_object = {}
    transaction_start_object = {
    "VASTerminalMode": 0x01,
    "ProtocolMode": 0x00
    }

    print('********************************')
    print('*  0 ->  exit                                         ')
    print('*  1 ->  setConfig                                         ')
    print('*  2 ->  getConfig                                         ')
    print('*  3 ->  setCAPK                                           ')
    print('*  4 ->  getCAPK                                           ')
    print('*  5 ->  deleteCAPK                                     ')
    print('*  6 ->  getPollingModes                            ')
    print('*  7 ->  reset                                                 ')
    print('*  8 ->  getSerialNumber                            ')
    print('*  9 ->  getFWVersion                                 ')
    print('*  A ->  getPaymentAppletVersion           ')
    print('*  B ->  getVASAppletVersion                    ')
    print('*  C ->  startTransaction                             ')
    print('*  D ->  getTransactionStatus                    ')
    print('*  E ->  getTransactionResult                    ')
    print('*  F ->  cancelTransaction                         ')
    print('* 10 ->  getTransactionLog                         ')
    print('* 11 ->  clearTransactionLog                    ')
    print('* 12 ->  close                                               ')
    print('********************************')
    rs232 = RS232('COM4')
    while True:
        print(' ')        
        index = input('plz choose case: ')
        # setconfig
        if operator.eq(index, '1'):
            if rs232.setConfig(reader_config_object):
                print('set config OK')
            else:
                print('set config NOK')
            if rs232.close():
                print('close OK')
            else:
                print('close NOK')

        # getconfig
        if operator.eq(index, '2'):
            if rs232.setConfig(reader_config_object):
                print('set config OK')
            else:
                print('set config NOK')
            if rs232.getConfig():
                print('get config OK')
            else:
                print('get config NOK')
            if rs232.close():
                print('close OK')
            else:
                print('close NOK')

        # setCAPK
        if operator.eq(index, '3'):
            if rs232.setCAPK(CAPK_object):
                print('set CAPK OK')
            else:
                print('set CAPK NOK')
            if rs232.close():
                print('close OK')
            else:
                print('close NOK')

        # getCAPK
        if operator.eq(index, '4'):
            if rs232.getCAPK():
                print('get CAPK OK')
            else:
                print('get CAPK NOK')
            if rs232.close():
                print('close OK')
            else:
                print('close NOK')

        # deleteCAPK        
        if operator.eq(index, '5'):
            if rs232.deleteCAPK(CAPK_object):
                print('delete CAPK OK')
            else:
                print('delete CAPK NOK')
            if rs232.close():
                print('close OK')
            else:
                print('close NOK')

        # getPollingModes
        if operator.eq(index, '6'):
            if rs232.getPollingModes():
                print('get polling Modes OK')
            else:
                print('get polling Modes NOK')
            if rs232.close():
                print('close OK')
            else:
                print('close NOK')

        if operator.eq(index, '7'):
            if rs232.reset():
                print('reset OK')
            else:
                print('reset NOK')
            if rs232.close():
                print('close OK')
            else:
                print('close NOK')

        if operator.eq(index, '8'):
            if rs232.getSerialNumber():
                print('get SerialNumber OK')
            else:
                print('get SerialNumber NOK')
            if rs232.close():
                print('close OK')
            else:
                print('close NOK')

        if operator.eq(index, '9'):
            if rs232.getFWVersion():
                print('get FWVersion OK')
            else:
                print('get FWVersion NOK')
            if rs232.close():
                print('close OK')
            else:
                print('close NOK')

        if operator.eq(index, 'A') or operator.eq(index, 'a'):
            if rs232.getPaymentAppletVersion():
                print('get PaymentAppletVersion OK')
            else:
                print('get PaymentAppletVersion NOK')
            if rs232.close():
                print('close OK')
            else:
                print('close NOK')

        if operator.eq(index, 'B') or operator.eq(index, 'b'):
            if rs232.getVASAppletVersion():
                print('get VASAppletVersion OK')
            else:
                print('get VASAppletVersion NOK')
            if rs232.close():
                print('close OK')
            else:
                print('close NOK')

        if operator.eq(index, 'C') or operator.eq(index, 'c'):
            if rs232.startTransaction(transaction_start_object):
                print('start Transaction OK')
            else:
                print('start Transaction NOK')
            if rs232.close():
                print('close OK')
            else:
                print('close NOK')

        if operator.eq(index, 'D') or operator.eq(index, 'd'):
            if rs232.getTransactionStatus():
                print('get Transaction Status OK')
            else:
                print('get Transaction Status NOK')
            if rs232.close():
                print('close OK')
            else:
                print('close NOK')

        if operator.eq(index, 'E') or operator.eq(index, 'e'):
            if rs232.getTransactionResult():
                print('get Transaction Result OK')
            else:
                print('get Transaction Result NOK')
            if rs232.close():
                print('close OK')
            else:
                print('close NOK')

        if operator.eq(index, 'F') or operator.eq(index, 'f'):
            if rs232.cancelTransaction():
                print('cancel Transaction OK')
            else:
                print('cancel Transaction NOK')
            if rs232.close():
                print('close OK')
            else:
                print('close NOK')

        if operator.eq(index, '10'):
            if rs232.getTransactionLog():
                print('get TransactionLog OK')
            else:
                print('get TransactionLog NOK')
            if rs232.close():
                print('close OK')
            else:
                print('close NOK')

        if operator.eq(index, '11'):
            if rs232.clearTransactionLog():
                print('clear TransactionLog OK')
            else:
                print('clear TransactionLog NOK')
            if rs232.close():
                print('close OK')
            else:
                print('close NOK')

        if operator.eq(index, '12'):
            if rs232.close():
                print('close OK')
            else:
                print('close NOK')

        if operator.eq(index, '0'):
            break

def check_modules(modules):
    #installed_modules = sys.modules.keys()
    #installed_modules = os.spawn("pip freeze")
    #fin, fout = popen2.popen2("sort")
    installed_modules =  os.popen("pip freeze").read()
    for chk_mod in modules:
        m = re.search(chk_mod, installed_modules, 0)
        if m is not None:
            print(chk_mod + ' module already installed')
        else:
            os.system('pip install ' + chk_mod)

if __name__ == "__main__":
    #test_com()
    check_modules(['pyserial',])
    test_interface()
    
