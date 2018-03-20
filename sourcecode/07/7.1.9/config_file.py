#!/usr/bin/python
# -*- coding: UTF-8 -*-

# �������ļ�
import ConfigParser

config = ConfigParser.ConfigParser()
config.read("ODBC.ini")
sections = config.sections()                    # �������е����ÿ�
print "���ÿ飺", sections
o = config.options("ODBC 32 bit Data Sources")  # �������е�������
print "�����", o
v = config.items("ODBC 32 bit Data Sources")
print "���ݣ�", v
# �������ÿ�������������
access = config.get("ODBC 32 bit Data Sources", "MS Access Database")
print access
excel = config.get("ODBC 32 bit Data Sources", "Excel Files")
print excel
dBASE = config.get("ODBC 32 bit Data Sources", "dBASE Files")
print dBASE

# д�����ļ�
import ConfigParser

config = ConfigParser.ConfigParser()
config.add_section("ODBC Driver Count")             # ����µ����ÿ�
config.set("ODBC Driver Count", "count", 2)         # ����µ�������
f = open("ODBC.ini", "a+")
config.write(f)                                 
f.close()

# �޸������ļ�
import ConfigParser
config = ConfigParser.ConfigParser()
config.read("ODBC.ini")
config.set("ODBC Driver Count", "count", 3)
f = open("ODBC.ini", "r+")
config.write(f)     
f.close()

# ɾ�������ļ�
import ConfigParser
config = ConfigParser.ConfigParser()
config.read("ODBC.ini")
config.remove_option("ODBC Driver Count", "count")  # ɾ��������
config.remove_section("ODBC Driver Count")          # ɾ�����ÿ�
f = open("ODBC.ini", "w+")
config.write(f)     
f.close()


