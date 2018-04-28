#!/usr/bin/env python
# _*_ coding:utf-8 _*_


import re
import os

cmd = 'cls'
def main():
    re_match()
    re_group()
    re_sub()
    re_repl()
    re_compile()

    
def re_match():
    os.system(cmd)
    string = 'www.runoob.com'
    print(re.match('www', string).span())
    print(re.match('www', string).start())
    print(re.match('www', string).end())
    print(re.match('www', string).group())
    print('\n')

def re_group():
    os.system(cmd)
    line = "cats are smarter than dogs"
    match_obj = re.match(r'(.*) are (.*?) .*', line, re.M|re.I|re.DOTALL)
    if match_obj:
        print('group: ' + match_obj.group())  # same as group(0)
        print('group: ' + match_obj.group(0))
        print('group: ' + match_obj.group(1))
        print('group: ' + match_obj.group(2))
    else:
        print('match NOK')
    print('\n')

def re_search():
    os.system(cmd)
    line = "cats are smarter than dogs"
    search_obj = re.search(r'(.*) are (.*?) .*')
    if search_obj:
        print('group: ' + search_obj.group())
        print('group: ' + search_obj.group(0))
        print('group: ' + search_obj.group(1))
        print('group: ' + search_obj.group(2))
    else:
        print('search NOK')
    print('\n')

def re_sub():
    os.system(cmd)
    phone = '2004-959-599 #这是一个电话号码'

    #删除注释
    num = re.sub(r'#.*$', '', phone)
    print('num: ' + num)

    #移除非数字的号码
    num = re.sub(r'\D', '', phone)
    print('num: ' + num)
    print('\n')

def re_repl():
    os.system(cmd)
    def double(matched):
        value = int(matched.group('value'))
        return str(value*2)
    s = 'A23G4HFD567'
    result = re.sub(r'(?P<value>\d+)', double, s)
    print(result)
    print('\n')

def re_compile():
    #os.system(cmd)
    string = 'one12twothree34four'
    pattern = re.compile(r'\d+')
    m = pattern.match(string)
    print(m)
    m = pattern.match(string, 2, 10)
    print(m)
    m = pattern.match(string, 13, 15)
    print(m)
    m = pattern.search(string)
    print(m)
    print('\n')

def re_findall():
    pass

def re_finditer():
    pass

def re_split():
    pass

if __name__ == '__main__':
    main()
