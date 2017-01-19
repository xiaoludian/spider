# encoding:utf-8


"""
Detail: 爬取天猫评论图片 
Date:2017-01-18
"""

import requests
import re
import codecs
import json
import shutil
import os
import queue
import threading
import time

from bs4 import BeautifulSoup

   
class DownloadThread(threading.Thread):  
    def __init__(self, name, queue):  
        threading.Thread.__init__(self)
        self.name = name
        self.queue = queue  
        self.headers = {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:22.0) Gecko/20100101 Firefox/22.0'}
        
    def run(self):  
        while True:
            item_id, index, pic_url = self.queue.get()    
            if item_id == -1:
                print('{}号线程结束下载任务！'.format(self.name))
                break
            self.download_pic(item_id, index, pic_url) 
        
    def download_pic(self, item_id, index, pic_url): 
        r = requests.get(pic_url, stream=True, headers=self.headers)
        if r.status_code == 200:
            with open("{}/{}.jpg".format(item_id, index), 'wb') as f:  
                f.write(r.content) 
            print('{}号线程下载完了{}的第{}张图片！'.format(self.name, item_id, index))    
            
            
class Spider():
    def __init__(self, keyword='书包', page=1, thread_num=1):
        self.keyword = keyword
        self.page = int(page)
        self.thread_num = thread_num
        self.headers = {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:22.0) Gecko/20100101 Firefox/22.0'}
        self.queue = queue.Queue()
        self.thread_list = []
        for i in range(1, thread_num + 1):
            t = DownloadThread(i, self.queue)
            t.start()
            time.sleep(0.1)
            self.thread_list.append(t)
            
    def get_page(self):
        page_content = []
        for i in range(1, self.page + 1):
            headers = {
                'dnt': '1',
                'accept-encoding': 'gzip, deflate',
                'accept-language': 'zh-CN,zh;q=0.8',
                'user-agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 BIDUBrowser/7.6 Safari/537.36',
                'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'referer': 'https://www.tmall.com/',
                'x-devtools-emulate-network-conditions-client-id': 'E71A3B1E-17BF-4625-B82C-12CA56F8A091',
                'cookie': '_med=dw:1366&dh:768&pw:1366&ph:768&ist:0; cq=ccp%3D0; pnm_cku822=026UW5TcyMNYQwiAiwQRHhBfEF8QXtHcklnMWc%3D%7CUm5Ockt%2BR31Gf0B0SX1GciQ%3D%7CU2xMHDJ7G2AHYg8hAS8WKQcnCVU0Uj5ZJ11zJXM%3D%7CVGhXd1llXGlQalFoV2NealFlUm9Nc0Z4QXVMdE1ySXNGc096Rmg%2B%7CVWldfS0RMQU%2FBSUZLQ0jQyhPI3lSckxsUHUjcxYpDSZPAy17LQ%3D%3D%7CVmhIGC0XNwoqFigRJQU%2BAzoFJRknHCcHPQYzEy8RKhExCzQBVwE%3D%7CV25Tbk5zU2xMcEl1VWtTaUlwJg%3D%3D; cna=DhIbEAJDiD0CAd9JAq3YIKej; hng=; uc3=nk2=D8z%2BKjQw5l2cNCClYQ%3D%3D&id2=Vyh5TEpK2b63IQ%3D%3D&vt3=F8dARHXQkW5nkDrSgt8%3D&lg2=URm48syIIVrSKA%3D%3D; uss=UoCKFwGVAXy2RfYMRH4sJTnqoPD0WhrZZ0t%2BkAGVd6kjgTpaQynnjFqWb6I%3D; lgc=longchisihai1; tracknick=longchisihai1; t=065f9049497dc46304e0ef2f205ab13b; _tb_token_=ij9XnCdc7ScT; cookie2=c573c1a9195d5c9d5eedfd9257bc4cd8; l=AouLx-nMC/Ew8iCxC3mPeskhmyF0LJ-y; isg=Ajg4V_IdlBt2mPeCWwv_4BmQGuZrG5wrDbKWbnKoiHM2jd13CLLIuxTvMwjk',
            }
            
            page_dict = {'from': 'mallfp..pc_1_searchbutton',
                         'q': self.keyword,
                         's': 60 * (i - 1),
                         'type':'pc',
                         'style':'g',
                         'spm': '875.7931836/A.a2227oh.d100',
                         'sort':'s'
                         }
            
            r =requests.get('https://list.tmall.com/search_product.htm', params=page_dict, headers=headers)
            r.encoding = 'utf-8'
            page_content.append(r.text)
            
        return page_content

    def get_url_from_page(self, page_content):
        '''
        返回具体商品的url
        '''
        url_list = []
        bs = BeautifulSoup(page_content, 'html.parser')
        div_all = bs.find_all('div', attrs= {'data-id' :re.compile(r'\d+'),
                                             'class': 'product '}
                              )
        for div in div_all:
            url_list.append('https:' + div.a.get('href'))
            
        return url_list
    
    def get_pic_from_url(self, url):
        '''
        根据商品url返回当前商品的所有评论图片地址 
        '''
        itemID, sellerId = (re.findall(r'\?id=(\d+).*?&user_id=(\d+)', url))[0]
        print(itemID, sellerId)
        pic_url_list = []
        
        page_num = 1
        while True:
            items = {'itemId': itemID,
                     'sellerId': sellerId,
                     'order': '3',
                     'currentPage':page_num,
                     'append': '0',
                     'content': '1',
                     'picture': '1',
                     'itemPropertyIndex':'',
                     'userPropertyId':'',
                     'userPropertyIndex':'',
                     'rateQuery':'',
                     'location':'',
                     'needFold':'0',
                     'callback':'json'
                     }      
            r = requests.get('https://rate.tmall.com/list_detail_rate.htm', params=items)
            r.encoding = 'utf-8'       
            # 对文本进行部分格式化修改 满足json解析需求
            text = r.text.replace('json(', '')
            text = text.strip()[:-1]
            json_data = json.loads(text)
            
            if not ('rateDetail' in json_data and 'rateList' in json_data['rateDetail']):
                break

            rate_list = json_data['rateDetail']['rateList']
            if rate_list:
                for item in rate_list:
                    pic_list = item['pics']
                    for pic in pic_list:
                        pic_url_list.append('https:' + pic)
            
            page_num += 1

        return itemID, pic_url_list
       
    def makedirs(self, item_id):
        if os.path.exists(item_id):
            shutil.rmtree(item_id)
        os.makedirs(item_id)
        
    def start(self):
        page_content = self.get_page()

        page_url = []
        for index, page in enumerate(page_content):
            page_url += self.get_url_from_page(page)
            print('获得第{}个页面所有物品信息！'.format(index + 1))
        
        for url in page_url:
            item_id, pic_url_list = self.get_pic_from_url(url)
            
            if pic_url_list != []:
                print('开始下载{}的{}张图片!'.format(item_id, len(pic_url_list)))
                self.makedirs(item_id)             
                for index, pic_url in enumerate(pic_url_list, 1):
                    self.queue.put((item_id, index, pic_url))
                    
        for i in range(self.thread_num):
            self.queue.put((-1, -1, -1))
            
        for thread in self.thread_list:
            thread.join()
            
        print('done!')
        
if __name__ == '__main__':
    keyword = input('请输入要查询的物品:')
    page = input('请输入要查询的页数:')
    thread_num = 10
    spider = Spider(keyword, page, thread_num)
    spider.start()
