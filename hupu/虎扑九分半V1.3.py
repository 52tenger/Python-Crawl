#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
获取虎扑九分半全站图片
https://api.jfbapp.cn/pk/list
"""
"""
修正了目录存在时，代表已经下载该回合
修正了有可能请求为空时的类型错误
"""

import requests
import os
import time

#将Json类型转换为Python类型
import json 
#处理Json的语言
import jsonpath

headers = {
    "content-length":"89",
    "accept": "application/json, text/plain, */*",
    "origin": "https://pk.weilutv.com",
    "User-Agent":"user-agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3325.146 Safari/537.36",
    "content-type": "application/json;charset=UTF-8",
    "referer": "https://pk.weilutv.com/history",
    "accept-language": "zh-CN,zh;q=0.9",
}

def zhuaqu(url, post_data):
    """
    获取所有回合
    """
    response = requests.post(url, data=json.dumps(post_data), headers=headers)
    html = response.text
    jsonobj = json.loads(html)
    # print(jsonobj)

    #匹配pks下所有一级id元素，如果想匹配子级，则将[*]换成..
    #匹配所有回合id，只是一部分
    url_id = jsonpath.jsonpath(jsonobj, "$.pks[*].id")
    #匹配所有回合时间
    date = jsonpath.jsonpath(jsonobj, "$.pks[*].date")
    #匹配下次post请求头
    cursor = jsonpath.jsonpath(jsonobj, "$.cursor.id")
    #匹配是否是还能进行请求
    hasMore = jsonpath.jsonpath(jsonobj, "$.cursor.hasMore")
    return [url_id,date,cursor,hasMore]


def huihe(url_id):
    """
    获取每一回合的页面，即图片地址
    """
    #每个回合相片名初始值
    n=1
    #每个回合的url
    url = "https://api.jfbapp.cn/pk/" + url_id
    response = requests.get(url)
    html = response.text
    jsonobj = json.loads(html)
    image_url = jsonpath.jsonpath(jsonobj, expr="$.pings[*].game.image")
    subtitle = "虎扑九分半颜战" +jsonpath.jsonpath(jsonobj, expr="$.pk.subtitle")[0]
    print("------正在下载%s-------"%subtitle)
    #创建多级目录文件夹
    try:
        os.makedirs("虎扑\%s"%subtitle)
    except Exception:
        print("----该%s已存在"%subtitle)
    else:
        for image in image_url:
            writeimage(image, subtitle, n)
            n+=1

def writeimage(image, subtitle, n):
    """
    将图片写入到本地
    """
    response = requests.get(image).content
    filename = "%d.jpg"%n
    with open(r"虎扑\%s\%s"%(subtitle,filename),"wb+") as f:
        f.write(response)


def main():
    
    url = "https://api.jfbapp.cn/pk/list"
    post_data={}
    hasMore = True
    print("--开始----")
    #获取更多的回合id，相当于鼠标往下拉，网站采取的是ajax
    while hasMore:
        a = zhuaqu(url, post_data)
        url_id_list = a[0]
        # date = a[1][0]
        cursor = a[2][0]
        hasMore = a[3][0]
        post_data = {"cursor":cursor}
        # 防止得到的请求为布尔类型
        try:
            for url_id in url_id_list:
                huihe(url_id)
        except:
            pass



if __name__ == '__main__':
    start = time.clock()
    main()
    end = time.clock()
    time = end-start
    print("--结束----,共用时%.2f秒"%time)
