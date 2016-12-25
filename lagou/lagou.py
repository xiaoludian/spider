# encoding:utf-8

"""
Detail:获得拉勾网招聘信息  
Date:2016-12-25
"""

import requests
import urllib.parse
import json
import xlsxwriter

POSITION_URL = 'https://www.lagou.com/jobs/positionAjax.json?city={}&needAddtionalResult=false'
headers = {'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
           'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:22.0) Gecko/20100101 Firefox/22.0'}

TAG = ['companyFullName', 'companyShortName', 'positionName', 
       'education', 'salary', 'financeStage', 
       'companySize', 'industryField', 'companyLabelList']

TAG_NAME = ['公司名称', '公司简称', '职位名称', 
            '所需学历', '工资', '公司资质', 
            '公司规模', '所属类别', '公司介绍']


def read_page(page_num, city, keyword):
    '''读取每一页的信息'''
    
    # cookies里面不能有中文
    cookies = {'PRE_LAND': 'https://www.lagou.com',
               'index_location_city': urllib.parse.quote(city),
               'user_trace_token': '20161204103620-1d8f224d10f4408da2a9eb1103b8433c',
               'LGUID': '20161204103620-70c9a0ff-b9ca-11e6-b029-525400f775ce'
               }

    if page_num == 1:
        boo = 'true'
    else:
        boo = 'false'

    data = {'first': boo,
            'pn': page_num,
            'kd': keyword
            }

    url = POSITION_URL.format(city)
    r = requests.post(url, data=data, cookies=cookies, headers=headers)
    return r.text


def get_total_page_count(page):
    '''获得总页数'''
    page_json = json.loads(page)
    total_count = page_json['content']['positionResult']['totalCount']
    page_size = page_json['content']['pageSize']
    return (int(total_count) // int(page_size)) + 1


def read_tag(page):
    '''获得每一页每一个公司的信息'''
    page_json = json.loads(page)
    result = page_json['content']['positionResult']['result']

    for each in result:
        each_conpany_info = []
        for tag in TAG:
            '''把list拆分成字符串'''
            if not isinstance(each[tag], list):
                each_conpany_info.append(each[tag])
            else:
                each_conpany_info.append(','.join(each[tag]))
        yield each_conpany_info


def save_excel(fin_result, file_name):
    '''保存到excel'''
    workbook = xlsxwriter.Workbook('{}.xlsx'.format(file_name))
    worksheet = workbook.add_worksheet()

    worksheet.write_row('A1', TAG_NAME)

    for index, conpany_info in enumerate(fin_result):
        worksheet.write_row('A{}'.format(index + 2), conpany_info)

    workbook.close()


def main(city, keyword):
    # 获得首页内容
    main_page_content = read_page(1, city, keyword)

    # 获得总页数
    total_page_count = get_total_page_count(main_page_content)

    fin_result = []

    for i in range(1, total_page_count + 1):
        page = read_page(str(i), city, keyword)
        for each_conpany_info in read_tag(page):
            fin_result.append(each_conpany_info)
         
    # 保存数据        
    save_excel(fin_result, city + keyword)
    
if __name__ == '__main__':
    # 要查询的数据
    city = '深圳'
    keyword = 'Python'

    main(city, keyword)
    
    print ('done!')   