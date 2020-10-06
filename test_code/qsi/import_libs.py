#!/usr/bin/python3

'''
python 导入依赖库的3种方式：
    1. import math
       导入整个模块，模块内变量和方法调用必须要用模块名调用，如：math.sin()

    2. from math import sqrt( or from math import *)
        导入模块math模块中的sqrt方法(或者导入math模块中的所有方法)，可以直接使用方法名调用，如：sqrt()

    3. from math import sqrt as st
        导入math模块中的sqrt方法，并将该方法起别名，则原有方法名不可使用，如：
        调用sqrt方法应该使用st(),再使用sqrt()会报错。
'''
