#!/usr/bin/env python
# _*_ coding:utf-8 _*_


import os
import shutil

def main():
    test_shutil()

def test_shutil():
    file = 'test_read_log'
    file1 = 'out.log'
    dir0 = ''
    dir1 = 'shutil'
    dir2 = 'shutil_a'

    #创建文件夹
    print(os.listdir(os.getcwd()))
    if os.access(dir1, os.F_OK):
        shutil.rmtree(dir1)   #dir 可不为空
    if os.access(dir2, os.F_OK):
        shutil.rmtree(dir2)   #dir 可不为空
    os.mkdir(dir1, 644)
    os.mkdir(dir2, 644)

    print(os.getcwd())
    files = os.listdir(os.getcwd())
    for x in files:
        if os.path.isdir(x):
            print('\td - ' + x)
        elif os.path.isfile(x):
            print('\tf - ' + x)
    print('\n')   
    #复制文件夹
    shutil.copytree(dir1, '.\\shutil\\shutil_copy')

    #移动文件夹
    shutil.move(dir2, dir1+'\\')
                
    #复制文件
    shutil.copy(file, dir1)
    shutil.copy(file, dir1+'\\test_dir_log')
    
    #移动文件
    if not os.access(file1, os.F_OK):
        try:
            tmp_fd = os.open(file1, os.O_CREAT)
        except NotImplementedError as e:
            print(e)
            return False
        else:
            os.close(tmp_fd)
    shutil.move(file1, dir1+'\\')
    os.chdir(dir1)
    curdir = os.listdir(os.getcwd())
    print(os.getcwd())
    for x in curdir:
        if os.path.isdir(x):
                print('\td - ' + x)
        if os.path.isfile(x):
                print('\tf - ' + x)
    print('\n')

    #重命名文件夹
    shutil.move('shutil_copy', 'shutil_copy2')
                
    #重命名文件
    shutil.move('test_dir_log', 'dir_log')
    curdir = os.listdir(os.getcwd())
    print(os.getcwd())
    for x in curdir:
        if os.path.isdir(x):
                print('\td - ' + x)
        if os.path.isfile(x):
                print('\tf - ' + x)
    print('\n')
    
    #删除文件
    os.unlink(file1)    #较os.remove适用范围更大
    #os.remove(file1)
    curdir = os.listdir(os.getcwd())
    print(os.getcwd())
    for x in curdir:
        if os.path.isdir(x):
                print('\td - ' + x)
        if os.path.isfile(x):
                print('\tf - ' + x)
    print('\n')
    
    #删除文件夹
    os.chdir('..')
    print(os.getcwd())
    shutil.rmtree('shutil')
    curdir = os.listdir(os.getcwd())
    for x in curdir:
        if os.path.isdir(x):
                print('\td - ' + x)
        if os.path.isfile(x):
                print('\tf - ' + x)
    print('\n')

if __name__ == '__main__':
    main()
