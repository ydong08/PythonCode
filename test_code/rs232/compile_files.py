#! /usr/bin/env python
# _*_ coding:utf8 _*_

import compileall
import py_compile
import shutil

"""
compile :
1. python -m file.py
2. compileall.compile_dir() #dir
3. py_compile.compile() #dir
"""
if __name__ == '__main__':
    compileall.compile_dir(r'./')
    shutil.copy(r'./__pycache__/rs232.cpython-36.pyc', r'./rs232.pyc')