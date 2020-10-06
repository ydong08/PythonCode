#!/usr/bin/python3

'''
二进制，八进制，16进制的表示和相互转换

'''

''' Python 进制数表示 '''
n1 = 1234      #十进制
n2 = 0b11101   #二进制
n3 = 0o127     #八进制
n4 = 0xF15     #十六进制

#其中 0b/0o/0x 与0B/0O/0F相同，即不区分大小写

''' Python 进制数间的转换 '''
print("\nbase10 -> basex")
print(bin(20))            #十进制转二进制
print(oct(1234))          #十进制转八进制
print(hex(54321))         #十进制转十六进制

print("\nbase2 -> basex")
print(oct(0b1101010101))  #二进制转八进制
print(int('11101', 2))    #二进制转十进制，0B前缀可有可无
print(hex(0b11011110101)) #二进制转十六进制

print("\nbase8 -> basex")
print(bin(0o127))         #八进制转二进制
print(int('0o126', 8))    #八进制转十进制
print(hex(0o125))         #八进制转十六进制

print("\nbase16 -> basex")
print(bin(0xF35AE))       #十六进制转二进制 
print(oct(0xF35AE))       #十六进制转八进制
print(int('0xF35AE', 16)) #十六进制转十进制，0x前缀可有可无




