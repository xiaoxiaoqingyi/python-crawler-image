#coding: utf-8

import time

import os

import re

import requests

import MySQLdb

from lxml import etree


# 文件存放目录名，相对于当前目录

DIR ="image"

#爬虫假装下正常浏览器请求

USER_AGENT ="Mozilla/5.0 (Windows NT 5.1) AppleWebKit/534.55.3 (KHTML, like Gecko) Version/5.1.5 Safari/534.55.3"



def fetch_image(url):

	try:

		headers ={

		"User-Agent": USER_AGENT,

#		"Referer": REFERER,

	#	"authorization": AUTHORIZATION

		}

		s = requests.get(url, headers=headers)

	except Exceptionas as e:

		print("fetch last activities fail. "+ url)

		raise e

	return s.content

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

def fetch_star_img():
   # 打开数据库连接
	db = MySQLdb.connect("localhost", "root", "lideyi", "star", charset='utf8' )
	# 使用cursor()方法获取操作游标 
	cursor = db.cursor()

	# SQL 查询语句
	sql = "SELECT * FROM star as s where s.download !=1 ORDER BY id ASC limit 1"

	# 执行SQL语句
	cursor.execute(sql)
	# 获取所有记录列表
	results = cursor.fetchall()

	if len(results) < 1:
		return 0

	for row in results:
		id = row[0]

		url = row[2]

		download = row[3]

		print("current url:"+url)
		
		content = fetch_activities(url)
		
		html = etree.HTML(content)

		#imglist = html.xpath('//div[@class="mainbox"]//div[@class="main"]//div[@class="leftbox"]//div[@class="contBox_js"]//div[@class="zhaopianBox"]//ul[@class="zp_list"]//li')

		imglist = html.xpath('//ul[@class="zp_list"]//li')

		#info = html.xpath('//ul[@class="geren_i"]//text()')

		#print(info)

		if len(imglist) < 1:
			# SQL 更新语句
			updatesql = "UPDATE star SET download = 1 WHERE id = '%d'" % (id)
			try:
			   # 执行SQL语句
			   cursor.execute(updatesql)
			   # 提交到数据库执行
			   db.commit()
			except:
			   # 发生错误时回滚
			   db.rollback()

			return fetch_star_img()
		
		for item in imglist:
			imgurl = item.xpath('img//@src')

			print("imgurl="+imgurl[0])
		
			s = fetch_image(imgurl[0])

			t = time.time()

			filename = str(id) + "_" + str(t) + ".jpg"

			with open(os.path.join(DIR, filename),"wb") as fd:

				fd.write(s)


			# SQL 更新语句
			updatesql = "UPDATE star SET download = 1 WHERE id = '%d'" % (id)
			try:
			   # 执行SQL语句
			   cursor.execute(updatesql)
			   # 提交到数据库执行
			   db.commit()
			except:
			   # 发生错误时回滚
			   db.rollback()

			insertsql = "INSERT INTO star_img(star_id,filename, url) VALUES (" + str(id) + ",'" + filename + "','" + imgurl[0] +"')"
			try:
			   cursor.execute(insertsql)
			   db.commit()
			except:
			   db.rollback()

	return 1
	
	

index = 1
while index == 1:

	index = fetch_star_img()

	time.sleep(1)