#!/usr/bin/env python
# -*- coding:utf-8 -*-


import requests
import time
import json
import jsonpath
# 线程模块
import threading
# 队列模块
from queue import Queue
import os

# 图片从1开始命名
global n 
n = 1

def douyu(num, imagequeue):
    """
    用于获取图片的url
    """
    baseurl = "https://mapi-yuba.douyu.com/wb/v3/digest?page="
    # 向下滑，进行翻页，初始为1 

    #实际url
    url = baseurl + str(num)

    # 模拟客户端浏览帖子请求头, 注意有时间戳
    headers = {
            "phone_model": "M5s",
            "client": "android",
            "phone_system": "5.1",
            "timestamp": "%.f"%time.time(),
            "User-Agent": "okhttp/3.9.0",
            }

    res = requests.get(url, headers=headers)
    print(res.status_code)
    html = json.loads(res.text)
    # 性别为女的昵称
    nickname = jsonpath.jsonpath(html, expr="$.data.list[?(@.sex==2)].nick_name")
    # 性别为女的帖子图片url
    image_link = jsonpath.jsonpath(html, expr="$.data.list[?(@.sex==2)].imglist[*].url")

    # 有可能只发贴，没有图片
    if image_link != False:
    # 将图片链接加入队列
        for image in image_link:
            imagequeue.put(image)
        print("获取第%s页结束"%num)

class Yuba(threading.Thread):
    """
    多线程下载
    """
    def __init__(self, imagequeue):
        # 继承父类初始化方法
        super().__init__()
        self.imagequeue = imagequeue

        #图片请求头
        self.headers = {"User-Agent":"user-agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3325.146 Safari/537.36",}

    def run(self):
        global n
        print("---启动图片线程--%s----"%self.name)
        while not self.imagequeue.empty():
            image_url = self.imagequeue.get()
            html = requests.get(image_url, self.headers).content
            filename = "%d.jpg"%n
            n = n+1
            with open(r"斗鱼鱼吧\%s"%filename,"wb+") as f:
                f.write(html)
            # 告诉线程已完成一个下载，否则会阻塞
            self.imagequeue.task_done()
        print("---结束图片线程--%s----"%self.name)

 

def main():
    # 创建图片队列
    imagequeue = Queue()
    num = int(input("请输入获取的页面数: "))
    n = 1
    while n<=num: 
        douyu(n, imagequeue)
        n+=1
        # time.sleep(1)
    # 创建存放图片文件夹
    try:
        os.mkdir("斗鱼鱼吧")
    except Exception:
        print("--文件夹已创建----")        

    # 请求线程数
    thread_num = 10
    for thread_i in range(thread_num):
        # 创建请求回合线程
        thread = Yuba(imagequeue)
        thread.start()

    # 等待线程结束，主线程才能结束
    imagequeue.join()

    print("所有图片线程结束")

if __name__ == '__main__':
    start = time.clock()
    main()
    end = time.clock()
    time = end-start
    print("--结束----,共用时%.2f秒"%time)