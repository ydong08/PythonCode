#!/usr/bin/env python
# _*_ coding:utf-8 _*_

import os
import stat
import time
import shutil

def main():
    os_test()

def list_files():
    file_list = os.listdir(os.getcwd())
    for i in file_list:
        print('\t' + i )
        
def os_test():
    tmp = 'tmp'
    #获取当前工作目录
    dirs = os.getcwd()
    print(dirs)
    curdir = dirs[dirs.rfind("\\")+1:]
    print('curdir:  ' + curdir)
    print(os.getcwdb())
    
    #获取当前目录文件夹和文件
    list_files()
        
    #更改工作目录
    os.chdir('..')
    
    #获取当前工作目录
    print(os.getcwd())
    
    #获取当前目录文件夹和文件
    list_files()
    
    #创建文件夹
    os.chdir('os_test')
    print(os.getcwd())
    if os.path.exists(tmp):
        os.removedirs(tmp)
        
    os.mkdir(tmp, 644)   #mode is ignored on windows 
    file_list = os.listdir(os.getcwd())
    for x in file_list:
        print('\t' + x)
    if os.access(tmp, os.F_OK):
        print('tmp exist')
    if os.access(tmp, os.R_OK):
        print('tmp can read')
    if os.access(tmp, os.W_OK):
        print('tmp can write')
    if os.access(tmp, os.X_OK):
        print('tmp can execute')
        
    #重命名文件夹
    if os.access('tmp2', os.F_OK):
        os.removedirs('tmp2')
        print('del file tmp2 OK')
        
    os.rename(tmp, 'tmp2')   #rename
    file_list = os.listdir(os.getcwd())
    for x in file_list:
        print('\t' + x)
        if not os.path.isdir(x):
            shutil.copy(x, '.\\tmp2\\' + x)
    os.chdir(r'.\tmp2')
    print(os.getcwd())
     
    # 创建文件
    fd = os.open('tmp_file', os.O_CREAT)   #open 创建文件
    if fd is not None:
        print('create file tmp_file OK')
        os.close(fd)
    file_list = os.listdir(os.getcwd())
    for x in file_list:
        print('\t' + x)
        
    #查看文件信息
    print(os.stat('tmp_file'))
    #print(os.stat('tmp2'))
    print('\n')
    #print(os.statvfs('tmp_file'))
    #print(os.statvfs('tmp2'))
    
    #更改权限
    os.chmod('tmp_file', stat.S_IWRITE)

    #复制文件
    if os.access('tmp_file2', os.F_OK):
        os.unlink('tmp_file2')
    shutil.copy('tmp_file', 'tmp_file2')
    file_list = os.listdir(os.getcwd())
    for x in file_list:
        print('\t' + x)
    
    #删除原文件
    os.unlink('tmp_file')
    print('delete tmp_file')
    file_list = os.listdir(os.getcwd())
    for x in file_list:
        print('\t' + x)

    #查看新文件信息
    statinfo = os.stat('tmp_file2')
    print(statinfo)
    print('\n')
    
    #获取文件大小
    for x in statinfo:
        print(x)
    print(statinfo[6])
    
    #打开文件
    try:
        fd = os.open('tmp_file2', os.O_RDWR, 644)
        print(fd)
    except (NotImplementedError, FileNotFoundError) as e:
        print(e)
        return False
    else:
        if 0 < fd:
            print('os.open OK')
    #写入数据
    print(os.write(fd, 'os.write()\n'.encode('utf-8')))
    print(os.write(fd, 'os.write2()\n'.encode('utf-8')))
    
    #读取写入后文件
    os.lseek(fd, 0, 0)
    print(os.read(fd, 50))
    
    #裁剪文件为第二次写入前
    os.lseek(fd, 0, 0)
    os.truncate(fd, 11)   #truncate 调用后文件结尾符号改变为\r
    print(os.read(fd, 20))
    
    #关闭文件
    os.close(fd)

    #获取文件大小
    statinfo = os.stat('tmp_file2')
    print(statinfo[6])

    #删除文件
    file_list = os.listdir(os.getcwd())
    for x in file_list:
        print('\t'  + x)
    os.unlink('tmp_file2')
    #time.sleep(5)
    print(os.getcwd())
    file_list = os.listdir(os.getcwd())
    for x in file_list:
        print('\t'  + x)
    print('remove tmp_file2')
    #删除当前目录下的文件夹
    file_list = os.listdir(os.getcwd())
    for x in file_list:
        print('\t'  + x)
        if os.path.isdir(x):
            os.removedirs(x)
        elif os.path.isfile(x):
            os.remove(x)
    print('after remove')
    file_list = os.listdir(os.getcwd())
    for x in file_list:
        print('\t'  + x)
    #更改工作目录
    os.chdir('..')

    #删除之前工作目录
    os.removedirs('tmp2')
    file_list = os.listdir(os.getcwd())
    for x in file_list:
        print('\t'  + x)

if __name__ == '__main__':
    main()
