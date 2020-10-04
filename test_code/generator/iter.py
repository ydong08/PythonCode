#!/usr/bin/python3
#_*_ coding:utf-8 _*_

import itertools

class Iter:
    def __init__(self):
        self.start = -1
    def __iter__(self):
        return self
    def __next__(self):
        self.start += 2
        return self.start

class MyRange:
	def __init__(self, n):
		self.i = 1
		self.n = n

	def __iter__(self):
		return self

	def __next__(self):
		if self.i <= self.n:
			i = self.i
			self.i += 1
			return i
		else:
			#迭代器和生成器结束时抛stop异常
			raise StopIteration()

if __name__ == '__main__':
	i = Iter()
	for count in range(5):
		print(i.__next__())

	print("range(7)", list(range(7)))
	print("MyRange(7)", [i for i in MyRange(7)])

	"""生成器库的使用"""
	counter = itertools.count(start=7)  
	print("counter:", next(counter))



