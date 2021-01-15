#!/usr/bin/env python
# _*_ coding:utf8 _*_

class _OneKey(object):
    def __init__(self, key):
        self.key = key

class _TwoValue(object):
    def __init__(self, value0, value1):
        self.key = 'NULL'
        self.value0 = value0
        self.value1 = value1

def test_format():
    # 原样输出
    print('{} {}'.format('hello', 'world'))
    print('{} {}'.format(20, 20.01))
    print('{} {}'.format(0.123, 1+3j))

    # 指定位置/ 顺序
    print('{1} {0} {1}'.format(0.123, 1+3j))
    print('{1} {0} {0}'.format(20, 20.01))
    print('{1}{0}*{0}'.format(20, 20.01))

    # 指定名字
    print('{key} is {0}'.format('winter', key='name'))
    # 如果指定名字，则index不存在，索引1是不存在的
    #print('{1} is {0}'.format('winter', name='name'))

    # 通过变量元组设置参数
    wein = ('name', '*', 7, 'winter')
    print('{0[0]} {0[1]} {0[2]}'.format(wein))

    # 通过列表设置参数
    info_list = ['name', 'winter']
    print('{0[0]} is {0[1]}'.format(info_list))
    web_list = ['google', 'huawei']
    print('{0[0]} is {0[1]}, {1[0]} == {1[1]}'.format(info_list, web_list))
   
    # 通过字典设置参数
    info = {'key':'name', 'value':'winter'}
    print('{key} is {value}'.format(**info))
    web = {'us':'google', 'cn': 'huawei'}
    print('{key} is {value}, {us} == {cn}'.format(**info, **web))

    # 通过对象设置参数
    ance0 =  _OneKey('name')
    ance1 = _TwoValue('is', 'winter')
    #print('{}'.format(ance0))
    print('{0.key} {1.key} {1.value0}'.format(ance0, ance1))

def case_test():
    print('{0:b} {1:b}'.format(3, 5))
    print('{:b}'.format(11))
    print('{:d}'.format(11))
    print('{:o}'.format(11))
    print('{:#o}'.format(11))
    print('{:x}'.format(11))
    print('{:#x}'.format(11))
    print('{:#X}'.format(11))
    # 指定小数位数
    print('{:.2f}'.format(3.1415926))   #3.14
    print('{:02.2f}'.format(3.1415926))   #3.14
    print('{:+2.2f}'.format(3.1415926))   #+3.14
    print('{:-2.2f}'.format(3.1415926))   #3.14
    print('{:+.3f}'.format(-3.1415))
    print('{:.0f}'.format(2.7896))
    # 对齐
    print('{:0>5d}'.format(30))   #00030
    print('{:x<3d}'.format(30))   #30x
    print('{:x^4d}'.format(30))   #x30x

    print('{:>5d}'.format(30))   #   30
    print('{:<3d}'.format(30))   #30 
    print('{:^4d}'.format(30))   # 30 
    # 指定宽度对小数没有意义
    print('{:,}'.format(1000000))
    print('{:2%}'.format(0.123))
    print('{:3%}'.format(0.123))
    print('{:2%}'.format(0.127))
    print('{:2e}'.format(1000000))
    print('{:<4%}'.format(0.123))
    print('{:%}'.format(0.123))
    print('{:%}'.format(0.127))
    print('{:e}'.format(1000000))
    # 使用｛｝ 转义
    print('{} is {{0}}'.format('key'))


if __name__ == '__main__':
   # test_format()
    case_test()