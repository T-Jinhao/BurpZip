#!/usr/bin/python
# -*- encoding:utf-8 -*-
# author:Jinhao

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
import argparse
import itertools as its
from concurrent.futures import ThreadPoolExecutor


#攻击字典
a = "0123456789"                     #纯数字
b = "abcdefghijklmnopqrstuvwxyz"     #纯小写字母
c = b.upper()                        #纯大写字母
d = b+c                              #大小写字母混合
e = a+d                              #数字+字母组合



class BurpZip():
    def __init__(self,zipfile,file):
        self.file = zipfile
        self.Fpayload = file
        self.max_threads = 50                      # 最大线程数
        self.exitflag = 1  # 总开关
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
                self.f = self.zp.namelist()[-1]    #定义为最后一个文件，确保非目录，用以爆破测试
                self.fatherpath= self.FilePath()
                print("-"*35+"文件信息"+"-"*35+"\n")
                self.Run()                         #启动爆破
            except:
                print("出现错误")
                sys.exit()
        else:
            print("warning：该文件不是zip压缩包")
            sys.exit()

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

        payload=its.product(key,repeat=length)
        return payload





    def UnzipFileTest(self,pwd):
        '''
        解压最后一个文件
        :param pwd:传入密码
        :return: 成功与否
        '''
        #fatherpath = self.FilePath()          #获取传入文件的父目录

        try:
            self.zp.extract(self.f,path=self.fatherpath,pwd=pwd.encode())   #解压压缩包
            # print("ok")
            return pwd
        except:
            # print("no")
            return False


    def Run(self):
        '''
        爆破脚本
        :return:
        '''
        #f = self.zp.namelist()[0]    #先获取第一个文件
        res = self.UnzipFileTest(pwd="")
        if res != False:     #测试密码是否为空
            print("[ 该压缩包没有设置密码 ]")         #进行空密码打开
            sys.exit()
        else:
            print("***文件打开失败，文件存在密码，请输入密码:***\n")
            pwd=input("密码：（进行密码爆破则直接回车）")
            if pwd != "" :
                res = self.UnzipFileTest(pwd=pwd)
                if res:
                    print("[ 密码：{} ]".format(res))
                    sys.exit()
                else:
                    print("[ 密码不正确：{} ]".format(str(pwd)))
            if self.Fpayload:
                payload = self.load_payloads()
                if payload:
                    print("[ payload导入成功 ]")
                    self.TBURP(payload)
                else:
                    print("{}文件读取失败".format(self.Fpayload))
                    self.diy_payload()
            else:
                self.diy_payload()


    def diy_payload(self):
        '''
        自定义payload
        :return:
        '''
        key = input("请选择攻击字典：a纯数字，b纯小写字母，c纯大写字母，d大小写字母混合，e数字字母混合，默认e\n")
        length = input("请合理输入密码长度上限,默认8：\n")
        if key == "a":
            self.key = a
        if key == "b":
            self.key = b
        if key == "c":
            self.key = c
        if key == "d":
            self.key = d
        if key != "a" and key != "b" and key != "c" and key != "d":            #其余情况均选择最长字典
            self.key = e
        try:
            self.length = int(length)
        except:
            self.length = int("8")    #其余情况默认长度为8
        print("开始爆破：\n密码字典内容：" + self.key + "\n密码长度上限：" + str(self.length))
        self.ThreadRun()

    def load_payloads(self):
        '''
        导入payload
        :return:
        '''
        payloads = []
        F = open(self.Fpayload, 'r')
        for x in F:
            try:
                t = x.replace('\n', '')
                payloads.append(t)
            except:
                pass
        return payloads


    def Burp(self,key,length):
        '''
        调用PayLoad()，使用生成的密码进行爆破
        :param key: 密码字典
        :param length: 密码长度
        :return:
        '''

        Length = int(length)  #二分密码长度，减少爆破时间
        if(Length<3):
            for x in self.PayLoad(key, length):  # 遍历密码
                x = "".join(x)
                res = self.UnzipFileTest(pwd=x)
                if res:  # 若测试解压成功，则用当前密码进行全部解压
                    print("[ 密码：{} ]".format(res))
                    sys.exit()
        else:
            if(Length%2==1):
                RLength = Length/2    #右半部密码长度
                LLength = RLength+1   #左半部密码长度
            else:
                LLength = Length/2
                RLength = LLength
            LLength = int(LLength)
            RLength = int(RLength)
            print("线程"+str(length) + "：" + str(LLength) + "+" + str(RLength))

            for L in self.PayLoad(key,LLength):
                for R in self.PayLoad(key,RLength):
                    L = "".join(L)
                    R = "".join(R)      #类型转换
                    pwd = L+R
                    res = self.UnzipFileTest(pwd=pwd)
                    if res:
                        print("[ 密码：{} ]".format(res))
                        sys.exit()

            print("线程-" + str(length) + "已停止")
            return False  # 中断线程

    def TBURP(self,payload):
        '''
        爆破密码
        :param payload:
        :return:
        '''
        payload = payload
        with ThreadPoolExecutor(max_workers=500) as pool:
            results = pool.map(self.UnzipFileTest, payload)
        for result in results:
            if result:
                print("[ 密码 ：{} ]".format(result))
                sys.exit()

    def ThreadRun(self):
        '''
        每个线程跑特定长度的密码
        :return:
        '''

        self.exitflag = 1
        threads = []
        for i in range(1,self.length+1):
            if self.exitflag == 1:
                thread = threading.Thread(target=self.Burp,args=(self.key,i))    #启动爆破线程
                threads.append(thread)        #添加进线程池
            else:
                threads = []       #self.exitflag==0时 清空线程池
        for t in threads:
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
    ter_opt = {}
    if len(sys.argv) == 1:
        sys.argv.append('-h')
    parser = argparse.ArgumentParser(description='简易ZIP压缩包密码爆破工具',add_help=True)
    parser.add_argument('-f','--file',help='需要爆破的压缩包文件')
    parser.add_argument('-e',default=None,help='自定义的外部密码本')
    args = parser.parse_args()
    for opt,val in args._get_kwargs():
        ter_opt[opt] = val
    if not ter_opt['file']:
        sys.exit(1)
    else:
        R = BurpZip(ter_opt['file'],ter_opt['e'])
    print("[ 没有爆破出正确密码 ]")



if __name__ == "__main__":
    main()