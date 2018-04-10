#coding: utf-8

import time

import requests

from lxml import etree

import MySQLdb

STAR_URL = [
            # 'http://www.manmankan.com/dy2013/mingxing/A/',
			# 'http://www.manmankan.com/dy2013/mingxing/B/',
			# 'http://www.manmankan.com/dy2013/mingxing/C/',
			# 'http://www.manmankan.com/dy2013/mingxing/D/',
			# 'http://www.manmankan.com/dy2013/mingxing/E/',
			# 'http://www.manmankan.com/dy2013/mingxing/F/',
			# 'http://www.manmankan.com/dy2013/mingxing/G/',
			# 'http://www.manmankan.com/dy2013/mingxing/H/',
			# 'http://www.manmankan.com/dy2013/mingxing/I/',
			# 'http://www.manmankan.com/dy2013/mingxing/J/',
			# 'http://www.manmankan.com/dy2013/mingxing/K/',
			# 'http://www.manmankan.com/dy2013/mingxing/L/',
			# 'http://www.manmankan.com/dy2013/mingxing/M/',
			# 'http://www.manmankan.com/dy2013/mingxing/N/',
			# 'http://www.manmankan.com/dy2013/mingxing/O/',
			# 'http://www.manmankan.com/dy2013/mingxing/P/',
			# 'http://www.manmankan.com/dy2013/mingxing/Q/',
			# 'http://www.manmankan.com/dy2013/mingxing/R/',
			# 'http://www.manmankan.com/dy2013/mingxing/S/',
			# 'http://www.manmankan.com/dy2013/mingxing/T/',
			# 'http://www.manmankan.com/dy2013/mingxing/U/',
			# 'http://www.manmankan.com/dy2013/mingxing/V/',
			# 'http://www.manmankan.com/dy2013/mingxing/W/',
			# 'http://www.manmankan.com/dy2013/mingxing/X/',
			 'http://www.manmankan.com/dy2013/mingxing/Y/',
			 'http://www.manmankan.com/dy2013/mingxing/Z/'
		   ]

#爬虫假装下正常浏览器请求

USER_AGENT ="Mozilla/5.0 (Windows NT 5.1) AppleWebKit/534.55.3 (KHTML, like Gecko) Version/5.1.5 Safari/534.55.3"


def fetch_activities(url):

	try:

		headers ={

		"User-Agent": USER_AGENT,

		}

		s = requests.get(url, headers=headers)

	except Exception as e:

		print("fetch last activities fail. "+ url)

		raise e

    
	s.encoding = "gbk"
	return s.text

def fetch_star(content, tag):
	# 打开数据库连接
	db = MySQLdb.connect("localhost", "root", "lideyi", "star", charset='utf8' )

	# 使用cursor()方法获取操作游标 
	cursor = db.cursor()

	html = etree.HTML(content)

	
	
	starlist = html.xpath('//div[@class="i_cont"]//a')

	for item in starlist:
		name = item.xpath('text()')

		url = item.xpath('@href')
		url = "http://www.manmankan.com" + url[0]

		# SQL 插入语句
		sql = "INSERT INTO star(name,url,tag) VALUES ('" + name[0] + "','" + url + "','" + tag +"')"

		try:
		
			# 执行sql语句
			cursor.execute(sql)
			# 提交到数据库执行
			db.commit()
		except:
			# Rollback in case there is any error
			db.rollback()
			#print("db error")
			return 0


   

	# 关闭数据库连接
	db.close()

	pagelist = html.xpath('//div[@class="pag"]//a')
	
	return len(pagelist)


for item in STAR_URL:

	url = item
	index = 1
	while url is not None:

		print("current url: "+ url)
		
		content = fetch_activities(url)
		pageNum = fetch_star(content, url)
		if (pageNum - 2 - index > 0):
			index = index + 1
			url = item + "index_" + str(index) + ".shtml"
		else:
			url = None

		time.sleep(5)
	


