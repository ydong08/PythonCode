#!/env/bin/python
# _*_ coding:utf-8 _*_

"""
在一个生成器中，如果没有return，
则默认执行到函数完毕时返回StopIteration
"""
def gen():
    yield 1
`
g = gen()
print(next(g))
print(next(g))
