# encoding:utf-8

"""
Detail:获得花椒热门主播信息
Date:2016-12-08
"""

import sys
import os
import requests
import re
import pymysql
import xlsxwriter
import lxml
import time

from bs4 import BeautifulSoup


class DataBase(object):
    def __init__(self, data):
        self.data = data

    def get_mysql_conn(self):
        return pymysql.connect(host='127.0.0.1', 
                               user='root', 
                               passwd='123456', 
                               db='huajiao', 
                               charset='utf8mb4')

    def insert_data(self):
        conn = self.get_mysql_conn()
        cur = conn.cursor()
        for user_info in self.data:
            try:
                cur.execute('REPLACE INTO user( ' 
                            'FUserId, FUserName, FLevel, FFollow, ' 
                            'FFollowed, FSupported, FExperience, ' 
                            'FAvatar, FScrapedTime) ' 
                            'VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)', 
                            (int(user_info['FUserId']), 
                             user_info['FUserName'], 
                             int(user_info['FLevel']), 
                             int(user_info['FFollow']), 
                             int(user_info['FFollowed']), 
                             int(user_info['FSupported']), 
                             int(user_info['FExperience']), 
                             user_info['FAvatar'], 
                             user_info['FScrapedTime']))
                conn.commit()
            except Exception as e:
                print ('写入数据库失败')
            
        print ('插入完毕')


class WriteFile(object):
    _headings = ['用户ID', '昵称', '等级',
                 '关注数', '粉丝数', '赞数',
                 '经验值', '头像地址', '爬取时间']
    
    _column_name_list = ['FUserId', 'FUserName', 'FLevel',
                         'FFollow', 'FFollowed', 'FSupported',
                         'FExperience', 'FAvatar', 'FScrapedTime']    
    
    def __init__(self, data):
        self.data = data

    def write_data(self):
        workbook = xlsxwriter.Workbook('花椒.xlsx')
        worksheet = workbook.add_worksheet()
        
        worksheet.set_column('A:A', 20)        
        bold = workbook.add_format({'bold': True})

        worksheet.write_row('A1', self._headings, bold)
        
        index = 2
        for user_info in self.data:
            tmp_list = [user_info[column_name] 
                        for column_name in self._column_name_list]
            worksheet.write_row('A{}'.format(index), tmp_list)
            index += 1
        
        workbook.close()
        
        print ('写入完毕！')
        
        
class Spider(object):
    _headers = {'content-type': 'application/json',
                'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:22.0) Gecko/20100101 Firefox/22.0'}
    
    _url_list = ['http://www.huajiao.com/category/1000',
                 'http://www.huajiao.com/category/1000?pageno=2'
                 ]
    
    def get_page_obj(self, url, **argv):
        r = requests.get(url, headers=self._headers, params=argv)
        r.encoding = 'utf-8'
        return BeautifulSoup(r.text, 'lxml')  
    
    def get_time(self):
        return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
    
    def get_live_id(self, url):
        '''获得当前页面推荐的直播id'''
        r = requests.get(url, headers=self._headers)
        bsObj = BeautifulSoup(r.text, 'lxml')
        
        id_list = []
        for link in bsObj.find_all('div', class_='g-feed2'):
            new_page = link.a.get('href')
            # 通过寻找最后一个/的方法来获得id
            each_id = new_page[new_page.rfind('/') + 1:]
            id_list.append(each_id)
    
        return id_list

    def get_hot_liveid(self):
        '''获得花椒热门直播id'''
        live_id = []
        for url in self._url_list:
            live_id += self.get_live_id(url)
        
        return live_id    

    def get_user_id(self, live_id):
        '''根据直播id 获取花椒id 也就是用户id 
        因为直播id变得非常的快 所以用户id有可能获取不到'''
        url = 'http://www.huajiao.com/l/' + live_id
        obj = self.get_page_obj(url)
        
        # 根据<p class="author-id">ID XXXX</p>定位花椒id
        user_id_info = obj.find('p', class_='author-id').string
        user_id = re.findall(r'\d+', user_id_info)
        if user_id != []:
            return user_id[0]       
    
    def get_user_info(self, user_id):
        '''根据用户id 获取用户详细信息 如果爬取失败 返回{}'''
        url = 'http://www.huajiao.com/user/' + user_id
        print ('开始爬取: {}'.format(url))
        
        try:
            data = {}
            data['FUserId'] = user_id
            
            obj = self.get_page_obj(url)
            
            # 头像地址
            pic_path = obj.find('div', class_='avatar').img.get('src')
            data['FAvatar'] = pic_path
            
            # 获得昵称
            pattern = re.compile(r'^(.*?)的主页')
            name = pattern.findall(obj.title.string)[0]
            data['FUserName'] = name
            
            user_info = obj.find('div', class_='info-box')
            # 用户等级
            level = user_info.find('span', class_='level').string
            data['FLevel'] = level
            
            # 获得关注数 粉丝数 赞数 和经验值
            tmp = user_info.find_all('li')
            record = []
            for each in tmp:
                record.append(each.p.string)
            
            data['FFollow'] = record[0]
            data['FFollowed'] = record[1]
            data['FSupported'] = record[2]
            data['FExperience'] = record[3]
            
            # 爬取时间
            data['FScrapedTime'] = self.get_time()
            
            return data
        
        except Exception as e:
            print (e)
            return {}   
        
    def get_data(self):
        live_id_list = self.get_hot_liveid()
        user_info_list = []
        for live_id in live_id_list:
            user_id = self.get_user_id(live_id)
            user_info = self.get_user_info(user_id)
            if user_info != {}:
                user_info_list.append(user_info)
        
        return user_info_list
    
if __name__ == '__main__':
    if len(sys.argv) != 2 and sys.argv[1] not in ('db', 'file'):
        print ('Usage: python3 huajiao.py [db|file]')
        
    spider = Spider()
    data = spider.get_data()
    
    if sys.argv[1] == 'db':
        db = DataBase(data)
        db.insert_data()
        
    elif sys.argv[1] == 'file':
        file = WriteFile(data)
        file.write_data()
        
    
    