#!/usr/bin/env python
# _*_ coding:utf-8 _*_

import os
import shutil

def main():
    read_file()
    #write_file()


def write_file():
    files = open('test_log', 'wb+')
    if files is not None:
        #if not file.isatty():
          #  return False
        files.seek(0, 0)
        files.write(bytes('this is a sentence\n\tGoogle Android', 'utf-8'))
        files.write(('\n\t' + str(file.fileno())).encode('utf-8'))
        list_t = ['\n\t\tPython file operation', '\n\t\tTest function']
        string = ''.join(list_t)
        print(string)
        print(type(string))
        byte = string.encode('utf-8')
        print(byte)
        print(type(byte))
        files.write(byte)
        #file.writelines(byte)   #witelines function not support byte
        print(files.fileno())
        print(files.name)
        files.close()
        return True

def read_file():
    files_name = files_operation('test.log', 'test_read_log')
    files = open(files_name, 'r+')
    if files is None:
        print('open file NOK')
        return False
    files_size = 0
    read_size = 80
    while True:
        data = files.read(read_size)
        files_size += len(data)
        if len(data) < read_size:
            break
        print(data)
        
        

def files_operation(old_file, new_file):
    result = shutil.copy(old_file, new_file)
    print(result)
    if result is not None:
        print('rename file %s OK' % old_file)
        return result
    else:
        print('rename file NOK')
        return None


if __name__ == '__main__':
    main()

