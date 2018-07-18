#!/env/bin/python
# _*_ coding:utf-8 _*_


'''
生成器支持的方法:
close
send
throw
yield from
'''

def gen():
    yield 1
    yield 2
    yield 3
    yield 4

g = gen()
print(next(g))
print(next(g))
""" close """
g.close()
#print(next(g))
print('\n')

def gen2():
    value = 0
    while True:
        receive = yield value
        if receive == 'e':
            break
        value = 'got: %s' % receive

g = gen2()
print(g.send(None)) # start generator, or next(g)
print(g.send('aaa'))
print(g.send(3))
print(g.send('e'))


    
