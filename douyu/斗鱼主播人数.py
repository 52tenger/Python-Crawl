#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
统计斗鱼主播人数
url：https://www.douyu.com/directory/all
缺点：可能统计不准确，因为斗鱼关闭直播间之后，可能就不显示在上面url中了
"""

# 导入模拟浏览器
from selenium import webdriver
# 导入浏览器设置功能
from selenium.webdriver.chrome.options import Options
# 鼠标移动功能
from selenium.webdriver.common.action_chains import ActionChains
# 解析模块
from lxml import etree
import requests, time
# 测试模块，方便调试
import unittest

class Douyu(unittest.TestCase):
    # 初始化方法，必须是setUp()
    def setUp(self):
        # 浏览器设置
        chrome_options = Options()
        # 无头，默认打开浏览器
        chrome_options.add_argument("--headless")
        # 模拟chrome浏览器
        self.driver = webdriver.Chrome(options=chrome_options)
        # 统计主播人数，初始为0
        self.n = 0
        # 测试时的有效人数，只算有热度的直播间,可能开了播但是没人气，热度大于0就算有人气
        self.N =0

    # 测试方法必须有test字样开头
    def testDouyu(self):
        url = 'https://www.douyu.com/directory/all'
        # 请求
        self.driver.get(url)
        # 生成图片快照
        self.driver.save_screenshot("douyu.png")

        # 不断点击翻页
        while True:
            # 获取页面源码
            text = self.driver.page_source
            html = etree.HTML(text)
            print(html)
            # 主播名字
            dy_name = html.xpath('//div[@id="live-list-content"]//span[@class="dy-name ellipsis fl"]/text()')
            # 主播热度
            dy_num = html.xpath('//div[@id="live-list-content"]//span[@class="dy-num fr"]/text()')
            print()
            
            for name,num in zip(dy_name, dy_num):
                print(name, num)
                self.n = self.n + 1
                if num != str(0):
                    self.N =self.N + 1`

            #找到下一页的位置,源码
            element = html.xpath("//a[@class='shark-pager-next']/text()")

            #鼠标的下一页的位置，元素，鼠标可以操作
            try:
                element_s = self.driver.find_element_by_xpath("//a[@class='shark-pager-next']")
            except Exception:
                print("已到达最后一页")
                break

            if element[0] == "下一页":
                ActionChains(self.driver).move_to_element(element_s).perform()
                element_s.click()
                # 等待页面加载完,防止下个页面未完成，找不到定位
                time.sleep(1)


    # 测试结束执行的方法
    def tearDown(self):
        print("测试结束")
        print("主播总人数为%d"%self.n)
        print("正在开播人数%d"%self.N)

if __name__ == '__main__':
    # 启动测试模块
    unittest.main()