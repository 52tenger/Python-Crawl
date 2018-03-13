#-*- coding:utf-8 -*-
#use python3
"""
分析过程：
1、先获取所有参赛回合的id，采用post请求，由于每次请求之后需要根据请求的内容是否继续获取和以及获得下一次的请求头，无法使用多线程
2、请求每次比赛回合的url，可采取多线程。又因为是获取的是json数据，所有每个回合的图片地址也可以提取出来，因为已经是json数据，所以不用多线程进行数据处理了
3、下载每一回合的图片，可采取多线程
"""
"""
优点：采取多线程，图片爬取速度快
缺点：不能分文件夹保存图片，那样的话可以采取每回合都设置一个队列，再采取多线程
"""

__auther__ = "tenger"

import time
import os
import requests
import json
import jsonpath

# 线程模块
import threading
# 队列模块
from queue import Queue


class ThreadCrawlbase(threading.Thread):
    """
    爬取每个回合的json数据，并提取出来图片的url
    """


    def __init__(self, basequeue, pagequeue):
        # 调用父类的初始化方法
        super().__init__()
        self.basequeue = basequeue
        self.pagequeue = pagequeue
        self.headers = {"User-Agent":"user-agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3325.146 Safari/537.36",}

    def run(self):
        print("---启动采集线程--%s----"%self.name)
        # 因为url = self.basequeue.get()只会从队列里取一次url_id.所以这里需要加while True循环来取
        while not self.basequeue.empty():
            # 当url队列里没有url的时候这里会堵塞等待，只要有就取，里面可以包含参数
            url_id = self.basequeue.get()
            #每一回合的具体url
            url = "https://api.jfbapp.cn/pk" + "/" + url_id
            html = requests.get(url, headers=self.headers).text
            jsonobj = json.loads(html)
            # 每一回合的所有图片url列表
            image_url = jsonpath.jsonpath(jsonobj, expr="$.pings[*].game.image")

            # 将采集到的队列加入页面队列处理，下载每一回合的每一张图片
            for i in image_url:
                self.pagequeue.put(i)
            # 取过后队列的基数并没有减１（并没有减去刚取走的url），所以要在下面使用task_done()
            self.basequeue.task_done()
        print("---结束采集线程--%s----"%self.name)
        
    @classmethod
    def hupu(cls):
        """
        获取每个回合的urlid
        """
        # 起始url
        url = "https://api.jfbapp.cn/pk/list"

        headers = {"User-Agent":"user-agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3325.146 Safari/537.36",}

        #判断urlid是否能继续抓取
        hasMore = True
        #post请求数据
        data = {}
        url_list = []

        #便利请求，相当于鼠标向下面拉 
        while hasMore:
            response = requests.post(url, data=data, headers=headers)
            html = response.text
            jsonobj = json.loads(html)
            url_id = jsonpath.jsonpath(jsonobj, "$.pks[*].id")
            #每次累加请求获取的回合id
            # print(url_id)
            try:
                url_list = url_list + url_id
            except TypeError:
                print("---下拉完成----") 
            cursor = jsonpath.jsonpath(jsonobj, "$.cursor.id")[0]
            data = {"cursor": cursor}
            #匹配是否是还能进行请求
            hasMore = jsonpath.jsonpath(jsonobj, "$.cursor.hasMore")[0]
            # print(hasMore)
        #返回urlid列表
        return url_list

class ThreadCrawlimage(threading.Thread):
    def __init__(self, pagequeue):
        super().__init__()
        self.pagequeue = pagequeue
        self.headers = {"User-Agent":"user-agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3325.146 Safari/537.36",}

    def run(self):
        global n
        print("---启动图片线程--%s----"%self.name)
        while not self.pagequeue.empty():
            image_url = self.pagequeue.get()
            html = requests.get(image_url, headers=self.headers).content
            filename = "%d.jpg"%n
            n = n+1
            with open(r"虎扑多线程\%s"%filename,"wb+") as f:
                f.write(html)
            self.pagequeue.task_done()
        print("---结束图片线程--%s----"%self.name)

# 图片从1开始命名
global n 
n = 1


def main():
    try:
        os.mkdir("虎扑多线程")
    except Exception:
        print("--文件夹已创建----")
    url_list = ThreadCrawlbase.hupu()

    # 创建一个可以容纳无数的队列，若里面有数字，则表示可以容纳几个值
    # 请求每个回合URL的队列,得到图片json数据
    basequeue = Queue()

    # 放入需要请求回合的队列
    for url in url_list:
        basequeue.put(url)

    # 每个回合页面的图片请求
    pagequeue = Queue()

    # 创建锁
    # lock = threading.Lock()

    # 每回合请求线程数
    thread_num = 5
    for thread_i in range(thread_num):
        # 创建请求回合线程
        thread = ThreadCrawlbase(basequeue, pagequeue)
        # 设置守护线程，主线结束后，子线程不管结没结束，都要跟着结束,一般不设置
        # thread.setDaemon(True)
        thread.start()

    # 主线程等待basequeue队列完成之后再执行
    basequeue.join()
    print("------所有的采集线程结束-----")

    #请求图片的线程
    thread_i_num = 20
    for thread_i in range(thread_i_num):
        # 创建请求回合线程
        thread = ThreadCrawlimage(pagequeue)
        # 设置守护线程，主线结束后，子线程不管结没结束，都要跟着结束,一般不设置
        # thread.setDaemon(True)
        thread.start()

    pagequeue.join()
    print("-----所有的下载线程结束-----")

    print("--主线程结束--")



if __name__ == '__main__':
    start = time.clock()
    main()
    end = time.clock()
    time = end-start
    print("--结束----,共用时%.2f秒"%time)
