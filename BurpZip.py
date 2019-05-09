#!/usr/bin/python
# -*- encoding:utf-8 -*-

'''
一键爆破压缩包脚本
先读取一个压缩文件，判断是否为压缩文件：识别错误的文件和伪加密文件
提取内部文件名，打开
若存在密码，构造密码爆破（多线程）
'''

import sys
import zipfile
import os
import threading
import time


#攻击字典
a="0123456789"                     #纯数字
b="abcdefghijklmnopqrstuvwxyz"     #纯小写字母
c=b.upper()                        #纯大写字母
d=b+c                              #大小写字母混合
e=a+d                              #数字+字母组合



class BurpZip():
    def __init__(self,name):
        self.file = name
        #self.threads_max=10
        self.OpenFile()                          #打开压缩包
        self.exitflag =1                          #总开关

    def OpenFile(self):
        '''
        打开压缩包，输出基本信息
        :return:
        '''
        if zipfile.is_zipfile(self.file):         #检测是否为压缩包
            try:
                self.zp = zipfile.ZipFile(self.file)
                print("-"*35+"文件信息"+"-"*35+"\n")
                print(self.zp.printdir())          #输出压缩包文件信息
                self.f = self.zp.namelist()[-1]    #定义为最后一个文件，确保非目录，用以爆破测试
                self.fatherpath= self.FilePath()
                print("-"*35+"文件信息"+"-"*35+"\n")
                # self.Run()                         #启动爆破
            except:
                print("出现错误")
                exit()
        else:
            print("warning：该文件不是zip压缩包")
            exit()

    def FilePath(self):
        '''
        获取文件父目录路径
        :return: 文件父目录
        '''
        path = os.path.abspath(self.file)                 #获取文件绝对路劲
        father_path = os.path.abspath(os.path.dirname(path) + os.path.sep + ".")      #截取父目录
        return father_path


    def PayLoad(self,key,length):
        '''
        穷举密码
        :param key: 密码字典
        :param length: 生成指定密码长度
        :return:密码
        '''

        if (length == 1):
            for x in key:
                yield x
        else:
            for x in key:
                for y in self.PayLoad(key, length - 1):   #循环生成指定长度密码
                    yield x + y




    def UnzipFileTest(self,pwd):
        '''
        解压最后一个文件
        :param pwd:传入密码
        :return: 成功与否
        '''
        #fatherpath = self.FilePath()          #获取传入文件的父目录

        pwd=pwd.encode()
        #print(pwd)

        try:
            self.zp.extract(self.f,path=self.fatherpath,pwd=pwd)   #解压压缩包
            # print("ok")
            return True
        except:
            # print("no")
            return False

    def UnzipFile(self,pwd):
        '''
        解压全部文件
        :param pwd: 解压密码
        :return:
        '''
        fatherpath = self.FilePath()  # 获取传入文件的父目录
        pwd = pwd.encode()            # 需要转成字节型
        for f in self.zp.namelist():  # 解压成功则全部进行解压
            try:
                self.zp.extract(f, path=fatherpath, pwd=pwd)  # 解压
                print("[+  解压成功] - " + f )
            except:
                print("[X  解压失败] X " + f )
        print("压缩文件已全部解压，压缩包密码为：" + pwd.decode())
        self.exitflag = 0               #给各线程发出结束信号
        exit()
        return 0

    def Run(self):
        '''
        爆破脚本
        :return:
        '''
        #f = self.zp.namelist()[0]    #先获取第一个文件
        if self.UnzipFileTest(pwd=""):     #测试密码是否为空
            self.UnzipFile(pwd="")         #进行空密码打开
        else:
            print("***文件打开失败，文件存在密码，请输入密码:***\n")
            pwd=input("密码：（进行密码爆破则直接回车）")
            if pwd !="" and self.UnzipFileTest(pwd=pwd)==True:
                # if self.UnzipFileTest(pwd=pwd):       #若测试解压成功，即用当前密码进行全部解压
                self.UnzipFile(pwd=pwd)

            else:
                key=input("请选择攻击字典：a纯数字，b纯小写字母，c纯大写字母，d大小写字母混合，e数字字母混合，默认e\n")
                length=input("请合理输入密码长度上限,默认8：\n")
                if key == "a":
                    self.key=a
                if key == "b":
                    self.key=b
                if key == "c":
                    self.key=c
                if key == "d":
                    self.key=d
                if key !="a" and key !="b" and key !="c" and key !="d":            #其余情况均选择最长字典
                    self.key=e
                try:
                    self.length = int(length)
                except:
                    self.length = int("8")    #其余情况默认长度为8
                print("开始爆破：\n密码字典内容："+self.key+"\n密码长度上限："+str(self.length))
                self.ThreadRun()



    def Burp(self,key,length):
        '''
        调用PayLoad()，使用生成的密码进行爆破
        :param key: 密码字典
        :param length: 密码长度
        :return:
        '''

        Length=int(length)  #二分密码长度，减少爆破时间
        if(Length<3):
            for x in self.PayLoad(key, length):  # 遍历密码
                if self.exitflag == 0:
                    # print("线程强制终结")    #测试用
                    break
                if self.UnzipFileTest(pwd=x):  # 若测试解压成功，则用当前密码进行全部解压
                    self.UnzipFile(pwd=x)
                    print("*** 爆破完成 ***")
                    return False  # 中断线程
        else:
            if(Length%2==1):
                RLength=Length/2    #右半部密码长度
                LLength=RLength+1   #左半部密码长度
            else:
                LLength=Length/2
                RLength=LLength
            LLength=int(LLength)
            RLength=int(RLength)
            print("线程"+str(length)+"："+str(LLength)+"+"+str(RLength))

            for L in self.PayLoad(key,LLength):
                for R in self.PayLoad(key,RLength):
                    if self.exitflag==0:
                        break
                    if self.UnzipFileTest(pwd=L+R):
                        self.UnzipFile(pwd=L+R)
                        print("*** 爆破完成 ***")
                        return False  # 中断线程

            print("线程-" + str(length) + "已停止")
            return False  # 中断线程


    def ThreadRun(self):
        '''
        每个线程跑特定长度的密码
        :return:
        '''

        #self.exitflag=False        #线程终止标志
        self.threads=[]            #线程池
        for i in range(1,self.length+1):
            if self.exitflag ==1:
             thread=threading.Thread(target=self.Burp,args=(self.key,i))    #启动爆破线程
             self.threads.append(thread)        #添加进线程池
            else:
                self.threads = []       #self.exitflag==0时 清空线程池
        for t in self.threads:
            t.start()
        while 1:
            time.sleep(0.05)    #防止线程堵塞



    def FileClose(self):
        '''
        关闭文件
        :return:
        '''
        self.zp.close()



def main():
    x = sys.argv[1]            #获取文件名
    print("操作对象："+x)
    R=BurpZip(x)                 #启动
    R.Run()                      #进行爆破
    #R.FileClose()                #关闭文件


if __name__ == "__main__":
    main()