#!/usr/bin/env python
# _*_ coding:utf-8 _*_

import os
import shutil
import time

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
    files_name = files_rename('test.log', 'test_read_log')
    if files_name is None:
        return False
    try:
        files = open(files_name, 'rb+')
        log = open('out.log', 'w')
    except IOError as e:
        print('open file NOK' + e)
        return False
    files_size = 0
    read_size = 80
    files.truncate(5120)
    while True:
        #data = files.read(read_size)
        #'''
        if files_size < 10240:
            data = files.read(read_size)
            print('read:---%d: ' % files.tell(), end='')
            print(data)
        elif files_size < 20480:
            try:
                data = next(files)
            except StopIteration as e:
                data = ''
                print('exception: ', end='')
                print(e)
            else:
                print('next:---%d: ' % files.tell(), end='')
                print(data, file=log)
                log.close()
        elif files_size < 30720:
            data = files.readline()
            print('readline:---%d: ' % files.tell(), end='')
            print(data)
        elif files_size < 40960:
            data = files.readlines()   #return is list
            print('readlines:---%d: ' % files.tell(), end='')
            print(data)
         #'''
        files_size += len(data)
        #if len(data) < read_size:
        if len(data) == 0:
            print('TotalSize %d' % files_size)
            files.close()
            return True
        
    
def files_rename(old_file, new_file):
    if not os.path.exists(old_file):   #检测文件或文件夹是否存在
        return None
    if os.path.exists(new_file):   #检测文件或文件夹是否存在
        os.unlink(new_file)
    #time.sleep(5)
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

