#!/usr/bin/python3

'''
python 字符串连接的5种方法：
    1. 使用"+"，如：s = "hello" + "world"

    2. 直接连接，如：s="hello""world"
       
    3. 使用逗号(,)连接，如：print("hello","world")
        标准输出重定向到特定IO，如：
        from io import StringIO
        import sys
        old_stdout = sys.stdout #保存标准输出
        result = StringIO() #新建IO实例
        sys.stdout = result #将标准输出重定向到特定IO
        print("hello", "world")
        sys.stdout = old_stdout #恢复标准输出
        result_str = result.getvalue()
        print("用逗号连接： "， result_str)
        

python 字符串与非字符串连接的方法：
    1. import math
       导入整个模块，模块内变量和方法调用必须要用模块名调用，如：math.sin()

    2. from math import sqrt( or from math import *)
        导入模块math模块中的sqrt方法(或者导入math模块中的所有方法)，可以直接使用方法名调用，如：sqrt()


python 字符串与对象连接的方法：
    1. import math
       导入整个模块，模块内变量和方法调用必须要用模块名调用，如：math.sin()

    2. from math import sqrt( or from math import *)
        导入模块math模块中的sqrt方法(或者导入math模块中的所有方法)，可以直接使用方法名调用，如：sqrt()
'''
