#!/usr/bin/env python
# _*_ coding:utf-8 _*_

import keyword
import json
import operator
import binascii
import sys
import os
from random import *
from math import ceil, pi, e, exp, fabs, floor, sqrt, modf


def main():
    print(keyword.kwlist)
    print('\n')
    if func_param_eq('COM4'):
        print('com 4 is same')
    #test_int()
    #test_string()
    #test_tuple()
    #test_list()
    #test_set()
    #test_dict()
    misc_type()

def test_int():
    print('Int:')
    print(4+5)   #add
    print(4.3 - 2)
    print(3*7)
    print(2/4)   #get  a float
    print(2//4)   #get a integer
    print(17%3)
    print(2**5)

    print(abs(-100))
    print(ceil(3.5))
    print(ceil(3.0))   #get high value
    print(ceil(-3.5))
    print(ceil(-3.4))
    print(pi)
    print(e)
    print((3>5) - (3<5))   #same as cmp function
    print((6>5) - (6<5))
    print(exp(2))
    print(fabs(-10))
    print(floor(10.7))   #get low value
    print(round(4.678, 2))
    print(sqrt(3.14))
    print(pow(3.14, 2))
    print(modf(3.14))
    print(modf(-3.14))

    #随机函数
    tup = (1, 879, 907, 145, 987, 169)
    print(choice(tup))
    print(randrange(0, 10000, 38))
    print(random())
    print(float(random()))
    print(uniform(1000, 2000))
    
    num_tup = modf(uniform(1000, 2000))
    print(num_tup)
    #float -> str
    print(str(num_tup[0]))
    print(type(str(num_tup[0])))
    print(str(num_tup[1]))
    print(type(str(num_tup[1])))
    print(str(num_tup[1]).replace('.0', str(num_tup[0])[2:]))
    print('\n')

def test_string():
    print('String:')
    string = 'Hello World!'
    print(string)
    print(string[0])
    print(string[1:-2])
    print(string[2:5])
    print(string[2:])
    print(string*2)
    print(string+'Earth')

    string = 'earth'
    print(string.capitalize())
    
    print(string.count('e'))
    print(string)
    print('%s' % string[0])
    byte = string.encode('utf-8')
    print(byte)
    print('%#x' % byte[0])
    print(byte.decode())
    print(string.endswith('th'))
    string = 'earth\tface'
    print(string)
    print(string.expandtabs(4))   #tab替换为指定数目的空格
    print(string)
    print(string.find('face'))
    #print(string.index('faces'))  #diff with find, will raise a exception when not find str
   #print(shuffle(string))    #str not support shuffle
         
    #一致性测试
    string = ''
    print(string.isalnum())   #至少一个字符或数字
    string = 'abc890'
    print(string.isalnum())   #至少一个字符或数字
    string = 'abcdefg'
    print(string.isalpha())   #至少一个字符
    string = '0123908097546abc'
    print(string.isdigit())   #只有数字
    string = 'abcdefg'
    print(string.islower())   #至少一个字符
    string = 'ABCDEFG'
    print(string.isupper())  #至少一个字符
    print(string.istitle())   #至少一个字符
    
    #补齐
    print(string.ljust(10, 'F'))   #左对齐，右填充
    print(string.rjust(10, 'F'))   #右对齐，左填充
    print(string.center(6, '-'))   #字符居中，2边填充
    print(string.zfill(10))   #右对齐,补0

    #分割、剔除
    string = 'A\nBCD\rEF\r\nG'
    print(string.splitlines())
    print(string.strip('\n\r'))
    print(' '.join(string))   #根据指定字符分割string
    print('\n')

def test_tuple():
    print('Tuple:')
    tup = ('runoob', 786, 2.23, 'john', 70.2)
    tiny_tup = (234, 'Edword')
    other_list = [1, '2', '2345', 'John', '##']
    cmp_tup = (12, 2.3, 890, 901)
    one_tup = (100,)
    print(tup)
    print(tup[0])
    print(tup[1])
    print(tup[3])
    print(tup[2:5])
    print(tup[2:])
    print(tup*2)
    print(tup + tiny_tup)
    if operator.eq(tup, tiny_tup):
        print('tup is same as tiny_tup')
    else:
        print('tup is NOT same asxtiny_tup')
        
    print(tuple(other_list))
    print('tup len %d' % len(tup))
    print('tup max value:', end='')
    print(max(cmp_tup))
    print('tup min value:', end='')
    print(min(cmp_tup))
    print(one_tup)
    print('\n')

def test_list():
    print('List:')
    test_list = ['runoob', 7856, 2.35, 'john', 70.2]
    tiny_list = [123, 'Edword']
    print(test_list)
    print(test_list[0])
    print(test_list[1])
    print(test_list[3])
    print(test_list[1:3])
    print(test_list[2:])
    print(test_list*2)
    print(test_list + tiny_list)
    test_list.append('jian')
    print(test_list)
    test_list.append(tiny_list)
    print(test_list)
    test_list.append((12, '234'))
    print(test_list)
    test_list.append({'abc':3, 256:'capability', })
    print(test_list)
    test_list.append({'bcd', 'ber', 1024})
    print(test_list)
    print(test_list.count('jian'))
    print(test_list.count(123))
    print(test_list.index(7856, 0 , len(test_list)))
    print(test_list.index('john', 0 , len(test_list)))
    print(test_list.index('jian', 0 , len(test_list)))
    print(test_list.insert(test_list.index('jian')+1, 'ai'))
    print(test_list)
    print(test_list.pop())
    print(test_list)
    print(test_list.pop(0))
    print(test_list)
    print(test_list.append('123'))
    print(test_list.append('245'))
    print(test_list.append('123'))
    print(test_list.remove('123'))
    print(test_list)
    print(test_list.reverse())
    print(test_list)
    #print(test_list.sort())  #ensure element type same
    list2 = test_list.copy()
    print(list2)
    list2.clear()
    print(list2)
    #del test_list
    print(shuffle(test_list))   #shuffle only support list
    print(test_list)
    test_list.clear()
    print(test_list)
    print('\n')

def test_dict():
    print('Dict:')
    dicts = {}
    dicts['one'] = 'this is one'
    dicts[2] = 'this is two'
    tiny_dict = {'name':'john', 'code':6745, 'dept':18, 2:'two', 3:3, 'dict':dicts}
    print(dicts)
    print(dicts['one'])
    print(dicts[2])
    print(tiny_dict)
    print(tiny_dict.keys())
    print(tiny_dict.values())
    print(tiny_dict.get('name'))
    for i in tiny_dict.items():
        print(i[0], i[1])
    print(tiny_dict.items())
    print(tiny_dict.setdefault('age', 300))
    print(tiny_dict)
    print(tiny_dict.setdefault('age', 800))
    print(tiny_dict)
    print(tiny_dict.pop('dict'))
    print(tiny_dict)
    print(tiny_dict.popitem())
    print(tiny_dict)
    tmp_dict = {'1':1, '2':2, '3':3, 'name':'john2'}
    print(tiny_dict.update(tmp_dict))   #tmp_dict的dict的key值和tiny_dict的key有重复，则使用
                                                              #tmp_dict中该key对应的value覆盖tiny_dict对应key的value
    print(tiny_dict)
    print('\n')

def test_set():
    print('Set:')
    tiny_set = {'China', 'American', 'Brazile', 'French', 'English', 'French'}
    a = set('apple')
    b = set('pear')
    empty_set = set()
    print(tiny_set)
    print(empty_set)
    print(a)
    print(b)
    print(a-b)   #差集
    print(a|b)   #并集
    print(a&b)  #交集
    print(a^b)   #a&b不同时存在的元素
    print('\n')

def test_from_byte():
    num1 = int.from_bytes(b'12', byteorder = 'big')
    num2 = int.from_bytes(b'12', byteorder = 'little')
    print('(%s,'%'num1', num1, '),', '(%s,'%'num2', num2, ')')

def test_to_byte():
    byt = (95).to_bytes(1, byteorder = 'big')
    byte0 = (94).to_bytes(1, byteorder = 'big')
    byt0 = (1).to_bytes(2, byteorder = 'big')
    byt1 = (1024).to_bytes(2, byteorder = 'big')
    byt2 = (1024).to_bytes(10, byteorder = 'big')
    byt3 = (2048).to_bytes(10, byteorder= 'big')
    byt4 = (4096).to_bytes(10, byteorder= 'big')
    lis1 = ['byt1', 'byt2', 'byt3', 'byt4']
    lis2 = [byt1, byt2, byt3, byt4]
    lis3 = zip(lis1, lis2)
    dic = dict(lis3)
    print(byte0)
    print('\n')
    print(byt)
    print('\n')
    print(byt0)
    print('\n')
    print(dic)

def test_json():
    reader_config_object = {'RestoreResult':12345678,
                                            'TransactionLogging':True,
                                            'TransactionLogSize':1024
                                            }
    reader_config = bytes(json.dumps(reader_config_object), 'utf-8')
    print(reader_config)

def func_param_eq(com):
    if operator.eq(com, 'COM4'):
        print(com)
        x = 'a'
        y = 'b'
        print(x, end="");print(y, end="")
        print('中国')
        '''
        inp = input('plz input: ')
        if type(inp) == type(''):
            print('string')
        if isinstance(inp, str):
            print('string')
       
        del x
        print(x)
         '''
        print(sys.argv)
        print('\n')
        return True
    else:
        return False
        
    
def misc_type():
    tup_a = (1,3,5,7,9,11)
    list_b = ['beijing', 'nanjing', 'dongjing', 'xian', 'chengdu']
    dict_c = {'American':'NewYourk', 'China':'BeiJing','Russian':'Mosico'}
    set_d = {'people',10000,'province',34,(100,),['liantong','yidong','dianxin']}
    print(tup_a)
    print(list_b)
    print(dict_c)
    print(set_d)


if __name__ == '__main__':

    main()
