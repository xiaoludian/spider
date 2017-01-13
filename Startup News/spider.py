# encoding:utf-8

"""
Detail: 单线程 爬取Startup News网站所有链接 
Date:2017-01-13
"""

import re
import requests
import collections
import codecs

from bs4 import BeautifulSoup

headers = {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:22.0) Gecko/20100101 Firefox/22.0'}

queue = collections.deque()
url = 'http://news.dbanotes.net'
queue.append(url)

# 用来去重
visited = set()

cnt = 0

with codecs.open('url.txt', 'w', 'utf-8') as f:
    # BFS算法
    while queue and cnt <= 100000:
        url = queue.popleft()  
        
        visited |= {url} 
    
        print('已经抓取: ' + str(cnt) + '   正在抓取 <---  ' + url)
        print(url, file=f)
        cnt += 1
    
        try:
            r = requests.get(url, headers=headers, timeout=1)
        except Exception as e:
            print('链接{}超时!'.format(url))
            continue
        
        r.encoding = 'utf-8'
        # 正则表达式提取页面中所有队列        
        # 如果没有在待爬队列 且尚未被访问过 加入待爬队列
        linkre = re.compile('href=\"(.+?)\"')
        for url in linkre.findall(r.text):
            if ('http' in url) and (url not in queue) and (url not in visited):
                queue.append(url)
                print('加入队列 --->  ' + url)
                