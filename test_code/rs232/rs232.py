#! /usr/bin/env python3
# _*_ coding:utf-8 _*_

import re
import sys
import os
import time
import binascii
import operator
import serial
import json
import py_compile
import serial.tools.list_ports
from serial.serialutil import *

"""
operate on windows COM 
"""


def test_com():
    "test windows COM recv and send data"
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




global_msg_type = {'set_config':0xE0,
                                'get_config':0xE1,
                                'set_capk': 0xE2,
                                'get_capk': 0xE3,
                                'del_capk': 0xE4,
                                'get_poll_mode': 0xE5,
                                'reset': 0xE6,
                                'get_serial_num': 0xE7,
                                'get_fw_version': 0xE8,
                                'get_payment_version': 0xE9,
                                'get_vas_version': 0xEA,
                                'start_transaction': 0xEB,
                                'get_trans_status': 0xEC,
                                'get_trans_result': 0xED,
                                'cancel_transaction': 0xEE,
                                'get_trans_log': 0xEF,
                                'clear_trans_log': 0xF0,
                                'close': 0xF1
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
        self.retry_num = 3

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
            return None
        since = time.time()
        while (0 < self.instance.inWaiting()
                    and time.time() - since < timeout):
            data.extend(self.instance.read())
        return bytes(data)

    def __check_recv_ack(self):
        error_code = bytearray()
        retry_num = 0
        while retry_num < self.retry_num:
            data = self.__recv_data(self.recv_timeout)
            if data is None:
                return False
            if self.__check_msg(data):
                    error_code.extend(self.__get_data(data))  # ack
                    if operator.eq(error_code.decode('utf-8'), '00'):
                        print('recv msg OK')
                        return True
            else:
                retry_num += 1
        else:
            print("recv msg %d retry done, stop recv" % retry_num)
            return False

    def __clear_cache(self):
        if self.instance is not None:
            self.instance.flushInput()
            self.instance.flushOutput()

    def setConfig(self, reader_config_object):
        """ set static reader configuration """
        reader_config = bytes(json.dumps(reader_config_object), "utf-8")
        data_len = left_len = len(reader_config)
        retry_num = 0
        index = 0
        self.__clear_cache()
        while 0 < left_len:   #send segment
            if self.__msg_len < left_len:
                max_send_len = self.__msg_len
            else:
                max_send_len = left_len

            if self.__send_data(global_msg_type['set_config'], reader_config[index:index+max_send_len]):
                # recv response
                index += max_send_len
                left_len -= max_send_len
            else:
                print('send request msg NOK, stop')
                break

        if 0 == left_len:
            print('send request msg[%d] OK' % data_len)
            return True
        else:
            return False

        while retry_num < self.retry_num:
            data = self.__recv_data(self.recv_timeout)
            if data is None:
                return False
            if operator.eq(data, 'ACK'):  # ack
                print('recv msg OK')
                return True
            else:
                retry_num += 1
        else:
            print("recv msg %d retry done, stop recv" % retry_num)
            return False

    def getConfig(self):
        """ get current config values """
        reader_config = {}
        self.__clear_cache()
        if self.__send_data(global_msg_type['get_config'], None):
            retry_num = 0
            while retry_num < self.retry_num:
                data = self.__recv_data(self.recv_timeout)
                if data is None:
                    return None
                if 0 < data.__len__():
                    if self.__check_msg(data):
                        reader_config = json.loads(self.__get_data(data))
                        print('recv msg OK')
                        break
                else:
                    retry_num += 1
            else:
                print("recv msg %d retry done, stop recv" % retry_num)
        return reader_config

    #@property
    def getCAPK(self):
        """  CAPK info """
        capk_tuple = ()
        self.__clear_cache()
        if self.__send_data(global_msg_type['get_capk'], None):
            retry_num = 0
            while retry_num < self.retry_num:
                data = self.__recv_data(self.recv_timeout)
                if data is None:
                    return None
                if 0 < data.__len__():
                    if self.__check_msg(data):
                        capk_config = json.loads(self.__get_data(data))
                        if isinstance(capk_config, dict):
                            for x in range(len(capk_config)):
                                if isinstance(x, dict):
                                    tmp_tuple = tuple(x)
                                    capk_tuple += tmp_tuple
                        print('recv msg OK')
                        break
                else:
                    retry_num += 1
            else:
                print("recv msg %d retry done, stop recv" % retry_num)
        return capk_tuple

    def setCAPK(self, CAPK_object):
        """ set CAPK """
        capk_config = bytes(json.dumps(CAPK_object), "utf-8")
        data_len = left_len = len(capk_config)
        max_send_len = 0
        index = 0
        self.__clear_cache()
        while 0 < left_len:   #send segment
            if self.__msg_len < left_len:
                max_send_len = self.__msg_len
            else:
                max_send_len = left_len

            if self.__send_data(global_msg_type['set_config'], capk_config[index:index+max_send_len]):
                # recv response
                index += max_send_len
                left_len -= max_send_len
            else:
                print('send request msg NOK, stop')
                break
        if 0 == left_len:
            print('send request msg[%d] OK' % data_len)
            return True
        else:
            return False

        while retry_num < self.retry_num:
            data = self.__recv_data(self.recv_timeout)
            if data is None:
                return False
            if operator.eq(data, 'ACK'):  # ack
                print('recv msg OK')
                return True
            else:
                retry_num += 1
        else:
            print("recv msg %d retry done, stop recv" % retry_num)
            return False

    def deleteCAPK(self, CAPK_object):
        """ delete CAPK """
        capk_config = bytes(json.dumps(CAPK_object), "utf-8")
        data_len = left_len = len(capk_config)
        max_send_len = 0
        index = 0
        self.__clear_cache()
        while 0 < left_len:   #send segment
            if self.__msg_len < left_len:
                max_send_len = self.__msg_len
            else:
                max_send_len = left_len

            if self.__send_data(global_msg_type['del_capk'], capk_config[index:index+max_send_len]):
                # recv response
                index += max_send_len
                left_len -= max_send_len
            else:
                print('send request msg NOK, stop')
                break
        if 0 == left_len:
            print('send request msg[%d] OK' % data_len)
            return True
        else:
            return False

        while retry_num < self.retry_num:
            data = self.__recv_data(self.recv_timeout)
            if data is None:
                return False
            if operator.eq(data, 'ACK'):  # ack
                print('recv msg OK')
                return True
            else:
                retry_num += 1
        else:
            print("recv msg %d retry done, stop recv" % retry_num)
            return False


    def getPollingModes(self):
        """ get supported polling modes """
        if self.__send_data(global_msg_type['get_poll_mode'], None):
            # recv response
            polling_mode = bytearray()
            retry_num = 0
            while retry_num < self.retry_num:
                data = self.__recv_data(self.recv_timeout)
                if data is None:
                    return None
                if 0 < data.__len__():
                    if self.__check_msg(data):
                        polling_mode.extend(self.__get_data(data))
                        print('recv msg OK')
                        return  polling_mode.decode('utf-8')
                else:
                    retry_num += 1
            else:
                print("recv msg %d retry done, stop recv" % retry_num)
            return None

    def reset(self):
        """ reset or reboot terminal """
        if self.__send_data(global_msg_type['reset'], None):
            # recv response
            if self.__check_recv_ack():
                return True
            else:
                return False
        else:
            print('send request msg NOK, stop')
            return False

    def getSerialNumber(self):
        """ get terminal serial number """
        if self.__send_data(global_msg_type['get_serial_num'], None):
            # recv response
            serial_number = bytearray()
            retry_num = 0
            while retry_num < self.retry_num:
                data = self.__recv_data(self.recv_timeout)
                if data is None:
                    return None
                if 0 < data.__len__():  # ack
                    if self.__check_msg(data):
                        serial_number.extend(self.__get_data(data))
                        print('recv msg OK')
                        return serial_number.decode('utf-8')
                else:
                    retry_num += 1
            else:
                print("recv msg %d retry done, stop recv" % retry_num)
                return None
        else:
            print('send request msg NOK, stop')
            return None

    def getFWVersion(self):
        """ FW version installed on terminal """
        if self.__send_data(global_msg_type['get_fw_version'], None):
            # recv response
            fw_version = bytearray()
            retry_num = 0
            while retry_num < self.retry_num:
                data = self.__recv_data(self.recv_timeout)
                if data is None:
                    return None
                if 0 < data.__len__():  # ack
                    if self.__check_msg(data):
                        fw_version.extend(self.__get_data(data))
                        print('recv msg OK')
                        return fw_version.decode('utf-8')
                else:
                    retry_num += 1
            else:
                print("recv msg %d retry done, stop recv" % retry_num)
                return None
        else:
            print('send request msg NOK, stop')
            return None

    def getPaymentAppletVersion(self):
        """ return payment applet version installed on reader """
        if self.__send_data(global_msg_type['get_payment_version'], None):
            # recv response
            payment_version = bytearray()
            retry_num = 0
            while retry_num < self.retry_num:
                data = self.__recv_data(self.recv_timeout)
                if data is None:
                    return None
                if 0 < data.__len__():  # ack
                    if self.__check_msg(data):
                        payment_version.extend(self.__get_data(data))
                        print('recv msg OK')
                        return payment_version.decode('utf-8')
                else:
                    retry_num += 1
            else:
                print("recv msg %d retry done, stop recv" % retry_num)
                return None
        else:
            print('send request msg NOK, stop')
            return None

    def getVASAppletVersion(self):
        """ return VAS applet version installed on reader """
        if self.__send_data(global_msg_type['get_vas_version'], None):
            # recv response
            vas_version = bytearray()
            retry_num = 0
            while retry_num < self.retry_num:
                data = self.__recv_data(self.recv_timeout)
                if data is None:
                    return None
                if 0 < data.__len__():  # ack
                    if self.__check_msg(data):
                        vas_version.extend(self.__get_data(data))
                        print('recv msg OK')
                        return vas_version.decode('utf-8')
                else:
                    retry_num += 1
            else:
                print("recv msg %d retry done, stop recv" % retry_num)
                return None
        else:
            print('send request msg NOK, stop')
            return None

    def startTransaction(self, transaction_start_object):
        """ put terminal in vas or payment mode """
        trans_config = bytes(json.dumps(transaction_start_object), "utf-8")
        data_len = left_len = len(trans_config)
        max_send_len = 0
        index = 0
        self.__clear_cache()
        while 0 < left_len:   #send segment
            if self.__msg_len < left_len:
                max_send_len = self.__msg_len
            else:
                max_send_len = left_len

            if self.__send_data(global_msg_type['start_transaction'], trans_config[index:index+max_send_len]):
                # recv response
                index += max_send_len
                left_len -= max_send_len
            else:
                print('send request msg NOK, stop')
                break

        if 0 == left_len:
            print('send request msg[%d] OK' % data_len)
            return True
        else:
            return False

        while retry_num < self.retry_num:
            data = self.__recv_data(self.recv_timeout)
            if data is None:
                return False
            if operator.eq(data, 'ACK'):  # ack
                print('recv msg OK')
                return True
            else:
                retry_num += 1
        else:
            print("recv msg %d retry done, stop recv" % retry_num)
            return False

    def getTransactionStatus(self):
        """ get transaction status inprogress, complete, or errorcode """
        trans_status = {}
        self.__clear_cache()
        if self.__send_data(global_msg_type['get_trans_status'], None):
            retry_num = 0
            while retry_num < self.retry_num:
                data = self.__recv_data(self.recv_timeout)
                if data is None:
                    return None
                if 0 < data.__len__():
                    if self.__check_msg(data):
                        trans_status = json.loads(self.__get_data(data))
                        print('recv msg OK')
                        break
                else:
                    retry_num += 1
            else:
                print("recv msg %d retry done, stop recv" % retry_num)
        return trans_status

    def getTransactionResult(self):
        """ get transaction status which consist of vas or payment status """
        trans_result = {}
        self.__clear_cache()
        if self.__send_data(global_msg_type['get_trans_result'], None):
            retry_num = 0
            while retry_num < self.retry_num:
                data = self.__recv_data(self.recv_timeout)
                if data is None:
                    return None
                if 0 < data.__len__():
                    if self.__check_msg(data):
                        trans_result = json.loads(self.__get_data(data))
                        print('recv msg OK')
                        break
                else:
                    retry_num += 1
            else:
                print("recv msg %d retry done, stop recv" % retry_num)
        return trans_result

    def cancelTransaction(self):
        """ cancel current transaction or vas mode and return to idle mode """
        if self.__send_data(global_msg_type['cancel_transaction'], None):
            # recv response
            if self.__check_recv_ack():
                return True
            else:
                return False
        else:
            print('send request msg NOK, stop')
            return False

    def getTransactionLog(self):
        """ return logObject which consist of a tuple of byte strings for each apdu
         logged duringvas or/ and payment transaction """
        trans_log = {}
        self.__clear_cache()
        if self.__send_data(global_msg_type['get_trans_log'], None):
            retry_num = 0
            while retry_num < self.retry_num:
                data = self.__recv_data(self.recv_timeout)
                if data is None:
                    return None
                if 0 < data.__len__():
                    if self.__check_msg(data):
                        trans_log = json.loads(self.__get_data(data))
                    print('recv msg OK')
                    break
                else:
                    retry_num += 1
            else:
                print("recv msg %d retry done, stop recv" % retry_num)
        return trans_log

    def clearTransactionLog(self):
        """ close log file for next logging session """
        if self.__send_data(global_msg_type['clear_trans_log'], None):
            # recv response
            if self.__check_recv_ack():
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
            if self.__check_recv_ack():
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
    reader_conﬁg_object    #python dictionary of key value pairs
    {
        "RestoreDefault":h,    # Restores all values to defaults
        "TransactionLogging":boolean,   # Flag to enable/disable transaction logging.
        "TransactionLogSize":h,   # Size of transaction log ﬁle on terminal
        "TransCurrencyCode":h,   # Per ISO 4217, indicated the currency code of the transaction
        "TransCurrencyExponent":h, #Indicates the position of the decimal point from the right of the transaction amount
        "TransType":h,   # Indicates the type of ﬁnancial transaction, Tag 9C
        
        "AmountAuthorized":h,  # Authorized amount of the transaction
        "AmountOther":h,   # Secondary amount associated with the transaction representing a cashback amount
        "TerminalCountryCode":h,   # Indicates the country of the terminal, represented according to ISO 3166
        "TerminalFloorLimit":h,   # Indicates the ﬂoor limit in the terminal in conjunction with the AID
        "TerminalCapabilities":h,   # Indicates the card data input, CVM, and security capabilities of the terminal
        "TerminalType":h,   # Indicates environment of the terminal, communications capability, and operational control
        "AdditionalTermCapabilities":h,   # Indicates the data input and output capabilities of the terminal
        "TerminalCTLSFloorLimit":h, # Indicates the Contactless ﬂoor limit in the terminal in conjunction with the AID
        "VisaTTQ":h,   # 9F66 Indicates Visa contactless MSD/EMV support, consumer device CVM
        "Timeout":time value in ms, # Timer used to end transaction if there is no interaction in the time out window.
         
        "mChipMobileSupport":h,   # Informs Card that Kernel supports extensions for mobile and requires OD_CVM
        "ExpressPayTerminalCapabilities":h, # 9F69 Indicates ExpressPay terminal capabilities
        "TerminalCTLSTransLimit":h, # Limit above which contactless transaction in not possible or must go online
        "CVMRequiredLimit":h,   # Limit above which Cardholder Veriﬁcation Method is required
        "TerminalActionCodeOnline":h,   # Reﬂects the acquirer-selected action to be taken upon analysis of the TVR
        "TerminalActionCodeDefault":h,   # Reﬂects the acquirer-selected action to be taken upon analysis of the TVR
        "TerminalActionCodeDenial":h,   # Reﬂects the acquirer-selected action to be taken upon analysis of the TVR
        "pollingMode":h,   # set reader polling mode, Auto Poll,Poll on Demand
        "pollingTechnology":h,   # set polling technololgy, 1 - Default, 2 - Type A, 3 - Type B, 4 - Type VAS, 5 - Type F
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
    
    transaction_start_object #python dictionary of key value pairs
    {
        "VASTerminalMode":h,   # See Appendix A for list of Modes
        "ProtocolMode":h,   # See Appendix B for list of Protocol Modes
        "AmountAuthorized":h,   # Authorized amount of the transaction
        "Timeout":time value in ms   # Timer used to end transaction if there is no interaction in the time out window.
        "TransDate":h,    # YYYYMMDD, Local date that the transaction was authorized
        "TransTime":time value in HHMMSS, # Local time that the transaction was authorized
        "TransType":h,   # Indicates the type of ﬁnancial transaction, Tag 9C
        "TransCurrencyCode":h,  # Per ISO 4217, indicated the currency code of the transaction
        "TerminalCountryCode":h,   # Per ISO 3166, Indicates the country of the terminal
        "AccountType":int,   # [00 Default-unspeciﬁed, 10 Savings, 20 Cheque/Debit, 30 Credit]
        "AmountOther":h,    # Secondary amt associated with the transaction representing a cashback amt
    }
    
    
    vas_result_object #python dictionary of key value pairs
    {
        'token' : h
        "data' : h
        'merchantID' : string
        'result code' : int
    }
    
    CAPK_object  #python dictionary of key value pairs
    {
        "RID":h,
        "CAPKIndex":h,
        "CAHashAlgoIndicator":h,
        "CAPKAlgoIndicator":h,
        "CAPKModulus":h,
        "CAPKExponent":h,
        "CAPKCheckSum":h,
    }
    
    
    transaction_result_object #python dictionary of key value pairs
    {
        "VASResults" : [
        (one for each VAS request in transaction)
        # Tuple of vas_result_object
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
    
    
    transaction_status_object    #python dictionary of key value pairs
    {
        transactionStatus:h,   # [00 inProgress, 01 Complete, 10 Error]
                                            # Add more states to determine if it"s VAS or Payment Status
                                            # Add more error codes per VAS and Payment specs
    }
    
    logObject       #python dictionary of key value pairs
    {
        getLog:string,   # Get transaction log ﬁle
        clearLog:boolean,    # Clear transaction logs
    }
    
    server_response_object     #tuple or python dictionary of key value pairs
    {
        # To deﬁne at a later date
        "Online Authorization/Results":string,# For simulating a response from the network
    }
        
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
    transaction_start_object = {}

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
    
