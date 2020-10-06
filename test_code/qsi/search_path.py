#!/usr/bin/python3

'''
python 设置搜索路径的3种方式：
    1. 设置PYTHONPATH环境变量(永久)
        a.在~/.profile 文件中添加"export PYTHONPATH=/user/defined/path:$PYTHONPATH"
        b.在命令行中执行：export PYTHONPATH=/user/defined/path:$PYTHONPATH
    2. 添加.pth文件(永久)
        在python安装目录的根目录中新建任意名称，但后缀为.pth的路径配置文件；如：
        在/usr/lib/python3.7 路径下新建pypath.pth，将搜索绝对路径以文本形式添加到该文件中
    3. 通过sys.path设置路径(临时)
        在要执行的代码中增加如下语句：sys.path.append("/home/python/libs"),
        只有该代码文件执行时，搜索path才会改变，且该path只对当前执行的文件有效。
'''
