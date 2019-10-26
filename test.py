#!/usr/bin/python
# -*- encoding:utf-8 -*-

import sys
import zipfile
import os
import random
import threading
import re
from time import time
# filename = "test.zip"
# path = os.path.abspath(filename)
# print(path)
# father_path = os.path.abspath(os.path.dirname(path) + os.path.sep + ".")
# print(father_path)
# path=os.path.splitext(filename)
# print(path)
# zp=zipfile.ZipFile(filename)
# for f in zp.namelist():
#
#     path=father_path+"\\"+f.replace("/","\\")
#     print(path)
#     zp.extract(f, path=father_path)
# print(zp.namelist())
# print(zp.namelist()[0])
# print(zp.namelist()[-1]+"22222")
# print(zp.infolist())
# print(zp.printdir())



def get_pwd(str, num):

    if (num == 1):
        for x in str:
            yield x
    else:
        for x in str:
            for y in get_pwd(str, num - 1):
                yield x + y

a = "abcdefghijklmnopqrstuvwxyz"
start=time()
for l in get_pwd(a,3):
    for r in get_pwd(a,2):
        print(l+r)
# for x in get_pwd(a,5):
#     print(x)
stop = time()
print(stop-start)







# b=a.upper()
# def test():
#     for i in range(500):
#         if i == 255:
#             exitflag=1

    # return "b"



# def xxx(name):
#     for i in range(500,1000):
#         print(str(i)+"  "+name)

# exitflag=0
# thread1=threading.Thread(target=test,args=())
#thread2=threading.Thread(target=test,args=())
# thread1.start()
#thread2.start()
# print(exitflag)
# if exitflag == 1:
#     print("adfa")
# print(thread1)
# key=input("key\n")
# print(type(key))
# print(key)
# key=key.encode()
# print(type(key))
# print(key)







