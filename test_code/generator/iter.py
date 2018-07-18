#!/env/bin/python
#_*_ coding:utf-8 _*_


class Iter:
    def __init__(self):
        self.start = -1
    def __iter__(self):
        return self
    def __next__(self):
        self.start += 2
        return self. start

i = Iter()
for count in range(5):
    print(next(i))



