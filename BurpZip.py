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
import _thread

#攻击字典
a="0123456789"                     #纯数字
b="abcdefghijklmnopqrstuvwxyz"     #纯小写字母
c=b.upper()                        #纯大写字母
d=b+c                              #大小写字母混合
e=a+d                              #数字+字母组合


class BurpZip():
    def __init__(self,name):
        self.file = name
        self.OpenFile()                          #打开压缩包


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
                for y in self.PayLoad(key, length - 1):
                    yield x + y





    def UnzipFileTest(self,pwd):
        '''
        解压文件
        :param pwd:传入密码
        :return: 成功与否
        '''
        fatherpath = self.FilePath()          #获取传入文件的父目录
        pwd=pwd.encode()
        #print(pwd)
        f = self.zp.namelist()[0]             #以第一个文件进行测试

        try:
            self.zp.extract(f,path=fatherpath,pwd=pwd)   #解压压缩包
            # print("ok")
            return True
        except:
            # print("no")
            return False

    def UnzipFile(self,pwd):
        fatherpath = self.FilePath()  # 获取传入文件的父目录
        pwd = pwd.encode()
        for f in self.zp.namelist():  # 解压成功则全部进行解压
            try:
                self.zp.extract(f, path=fatherpath, pwd=pwd)  # 解压
                print("[+] " + f + "   --解压成功")
            except:
                print("[+] " + f + "   --解压出错")
        print("压缩文件已全部解压，压缩包密码为：" + pwd.decode())
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
            print("文件打开失败，文件存在密码，请输入密码:\n")
            pwd=input("密码：（进行密码爆破则直接回车）")
            if pwd !="":
                if self.UnzipFileTest(pwd=pwd):
                    self.UnzipFile(pwd=pwd)
            else:
                key=input("请选择攻击字典：a纯数字，b纯小写字母，c纯大写字母，d大小写字母混合，e数字字母混合，默认e\n")
                length=input("请合理输入密码长度上限：\n")
                if key == "a":
                    self.key=a
                if key == "b":
                    self.key=b
                if key == "c":
                    self.key=c
                if key == "d":
                    self.key=d
                else:            #其余情况均选择最长字典
                    self.key=e
                try:
                    self.length = int(length)
                except:
                    self.length = int("15")    #其余情况默认长度为15
                print("开始爆破：\n密码字典内容："+self.key+"\n密码长度上限："+str(self.length))
                self.ThreadRun()


    def Burp(self,key,length):
        '''
        调用PayLoad()，使用生成的密码进行爆破
        :param key: 密码字典
        :param length: 密码长度
        :return:
        '''
        print("run")
        for x in self.PayLoad(key,length):
            if self.UnzipFileTest(pwd=x):
                self.UnzipFile(pwd=x)


    def ThreadRun(self):
        '''
        每个线程跑特定长度的密码
        :return:
        '''
        for i in range(self.length):    #跑特定长度的密码
            _thread.start_new_thread(self.Burp,(self.key,i,))


    def FileClose(self):
        self.zp.close()














def main():
    x = sys.argv[1]            #获取文件名
    print("操作对象："+x)
    R=BurpZip(x)                 #启动
    R.Run()                      #进行爆破
    R.FileClose()                #关闭文件


if __name__ == "__main__":
    main()
