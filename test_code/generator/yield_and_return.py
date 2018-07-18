#!/env/bin/python
# _*_ coding:utf-8 _*_

"""
在一个生成器中，如果遇到return,
在执行过程中 return，则直接抛出 StopIteration 终止迭代
"""
def gen():
    yield 'a'
    return
    yield 'b'

def gen2():
    yield 'a'
    yield 'b'
    return

"""
在一个生成器中，如果在return后返回一个值，
那么这个值为StopIteration异常的说明，不是程序的返回值
"""
def gen3():
    yield 'a'
    yield 'b'
    return 'over'

g = gen3()
print(next(g))
print(next(g))
try:
    print(next(g))
except StopIteration as e:
    print(e)
    

