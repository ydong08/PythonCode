''''
class test code
'''

#coding=utf-8

class Man:
	''' 
		class variables
		NOTE: 
			1. instance variables cannot change class variables
			2. can be add class or instance variables dynamicly
			3. instance have all class variables
	'''
	sex = 'male'


	''' init function, not constructor function '''
	def __init__(self):
		''' instance variables '''
		self.name = 'china'
		self.age = '5000'
		self.city = 'asia'


	'''
		instance method
		both class and instance can call this 'methodx'
		instance.method('HeNan')
		or
		Man.method(instance, 'HeNan')

	'''
	def method(self, index):
		print(index, self.sex, self.city)

	''' class method, only class can call this method '''
	@classmethod
	def class_method(cls, index):
		print(index, cls.sex)

	''' 
		same as method, both class and instance can call static_method
		however, it dosenot need self or cls parameter
	'''
	@staticmethod
	def static_method(index):
		print(index)


if __name__ == '__main__':
	Man.tall = '1000'
	Man.hands = 10

	print(Man.sex)
	print(Man.tall)
	print(Man.hands)

	man = Man()
	man.road = 'people'
	print(man.road)
	man.method('1')

	Man.method(man, '2')

	Man.class_method('3')

	Man.static_method('4')
	man.static_method('5')




