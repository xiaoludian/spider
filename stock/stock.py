# encoding:utf-8

"""
Detail:查询股票实时价格
利用的新浪股票接口，详见：
http://blog.csdn.net/simon803/article/details/7784682
Date:2016-12-11
"""

import sys
import os
import requests
import time
import queue
import argparse
import threading


class Workder(threading.Thread):
    '''多线程'''
    def __init__(self, work_queue, result_queue):
        threading.Thread.__init__(self)
        self.work_queue = work_queue
        self.result_queue = result_queue
        # 这里启动所有线程
        self.start()
    
    def run(self):
        while True:
            func, stock_code = self.work_queue.get()
            name, price = func(stock_code)
            if name != None and price != None:
                self.result_queue.put((name, price))
            # 所有数据已经获得  输出
            if self.result_queue.full():
                stock_list = []
                while not self.result_queue.empty():
                    stock_list.append(self.result_queue.get())
                    
                output_list = sorted(stock_list, key=lambda x: x[0])
                print ('***** start *****')
                for stock_info in output_list:
                    print (' '.join(list(stock_info)))
                print ('***** end *****')
                
            self.work_queue.task_done()
    
class Stock(object):
    '''股票类'''
    def __init__(self, stocks, thread_num):
        self.stocks = stocks
        self.threads = []
        self.work_queue = queue.Queue()
        self.__init_thread_poll(thread_num)
        
    def __init_thread_poll(self, thread_num):
        self.stock_list = self.stocks.split(',')
        self.result_queue = queue.Queue(maxsize=len(self.stock_list))
        for i in range(thread_num):
            self.threads.append(Workder(self.work_queue, self.result_queue))
       
    
    def start(self):
        '''开始爬取数据股票数据'''
        for stock_code in self.stock_list:
            self.work_queue.put((self.value_get, stock_code))
    
    @classmethod        
    def value_get(cls, stock_code):
        '''根据股票代码 获得股票名称和价格'''
        headers = {'content-type': 'application/json',
                   'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:22.0) Gecko/20100101 Firefox/22.0'}        
        
        slice_num = 23
        
        # 有时候用户输入的股票代码不正确 要处理错误情况
        url = 'http://hq.sinajs.cn/list=s_'
        r = requests.get(url + stock_code, headers=headers)
        req_list = r.text.split(',')
        try:
            name = req_list[0][slice_num:]
            price = req_list[1]
        except Exception as e:
            return None, None
        else:
            return name, price
    
if __name__ == '__main__':
    if len(sys.argv) == 1:
        sys.argv.append('--help')    

    parser = argparse.ArgumentParser()
    parser.add_argument("stocks", help=("股票代码,查询多个股票用逗号分隔,"
                                        "每个股票代码前面要加上(sz or sh)"))
    parser.add_argument("-n","--thread_number", type=int, default=1, help="线程数") 
    parser.add_argument("-t","--sleep_time", type=int, default=3, help="查询时间")      
    args = parser.parse_args()
    
    stocks = args.stocks
    thread_num = args.thread_number
    
    stock = Stock(stocks, thread_num)
    
    while True:
        stock.start()
        time.sleep(args.sleep_time)
    