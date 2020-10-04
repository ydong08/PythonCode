#! /usr/bin/python3
# _*_ coding:utf-8 _*_

def odd():
    n = 1
    while True:
        yield n
        n += 2

odd_num = odd()
count = 0
for i in odd_num:
    if 5 <= count:
        break
    print(i)
    count += 1
