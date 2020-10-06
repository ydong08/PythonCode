#!/usr/bin/python3

'''
python 字符串连接的5种方法：
    1. 使用"+"，如：s = "hello" + "world"

    2. 直接连接，如：s="hello""world"
       
    3. 使用逗号(,)连接，如：print("hello","world")
        标准输出重定向到特定IO，如：
        from io import StringIO
        import sys
        old_stdout = sys.stdout #保存标准输出
        result = StringIO() #新建IO实例
        sys.stdout = result #将标准输出重定向到特定IO
        print("hello", "world")
        sys.stdout = old_stdout #恢复标准输出
        result_str = result.getvalue()
        print("用逗号连接： "， result_str)

    4. 格式化方法
        s = '%s%s' % (s1, s2)
        print("格式化： ", s)

    5. 字符串对象的join方法
        s = "".join([s1, s2])
        print("join连接： ", s)
        

python 字符串与非字符串连接的方法：
    1. 使用加号("+")，字符串和非字符串不能通过"+"直接相连，需要使用str函数转换之后相加，如：
        n = 20
        s = s1 + str(n)

    2. 格式化方法
        n = 20
        v = 3.14
        s1 = "hello"
        s = '%s%d%.2f' %s (s1,n,v)

    3. 重定向(方法和字符串连接相同)

python 字符串与对象中特定的字符串连接的方法：
    1. class Myclass:
            def __str__(slef): #重写全局函数str
                return 'Myclass'
        
        s1 = 'hello'
        cls = Myclass()
        s = s1 + str(cls)
'''
