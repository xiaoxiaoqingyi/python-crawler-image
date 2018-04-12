#coding: utf-8

import time

import os

import re

import random

import requests

from lxml import etree

from aip import AipFace

import MySQLdb

#百度云 人脸检测 申请信息

#唯一必须填的信息就这三行

APP_ID ="11065567"

API_KEY ="5Qt8HG15XcNUzGc4RbbDIOWr"

SECRET_KEY ="nTri8NdrSavRyKjwKbjRTW0vj0LHx1hE"

# 文件存放目录名，相对于当前目录

DIR ="image"

# 过滤颜值阈值，存储空间大的请随意

BEAUTY_THRESHOLD =30

#如果权限错误，浏览器中打开知乎，在开发者工具复制一个，无需登录

#建议最好换一个，因为不知道知乎的反爬虫策略，如果太多人用同一个，可能会影响程序运行

#如何替换该值下文有讲述

AUTHORIZATION ="oauth c3cef7c66a1843f8b3a9e6a1e3160e20"



def face_detective(client, options, image):

	r = client.detect(image, options)

	if "result_num" not in r:
		return{}

	if r["result_num"]==0:
		#说明检测不到人脸，删了
		return{}


	for face in r["result"]:

		#人脸置信度太低

		if face["face_probability"]<0.6:

			return{}

		#真实人脸置信度太低

		if face["qualities"]["type"]["human"]<0.6:

			return{}

		#颜值低于阈值

		if face["beauty"]< BEAUTY_THRESHOLD:

			return{}

		return face


def aip_face_img(client, options):
   # 打开数据库连接
	db = MySQLdb.connect("localhost", "root", "lideyi", "star", charset='utf8' )
	# 使用cursor()方法获取操作游标 
	cursor = db.cursor()

	# SQL 查询语句
	sql = "SELECT * FROM star_img as s where s.ischeck !=1 ORDER BY id ASC limit 1"

	# 执行SQL语句
	cursor.execute(sql)
	# 获取所有记录列表
	results = cursor.fetchall()

	if len(results) < 1:
		return 0

	for row in results:
		id = row[0]

		filename = row[3]

		print("filename:"+filename)

		with open('image\\'+filename , 'rb') as f:
			
			image = f.read()
		
		face = face_detective(client, options, image)

		if len(face) > 1:
			updatesql = """
				UPDATE star_img SET ischeck=1,age=%f,beauty=%f,gender='%s',gender_probability=%f,
				face_width=%d,face_height=%d,face_probability=%f,rotation_angle=%d,
				yaw=%f,pitch=%f,roll=%f,human=%f,cartoon=%f
				WHERE id = %d
			"""% (face["age"], face["beauty"], face["gender"], face["gender_probability"],
				face["location"]["width"], face["location"]["height"], face["face_probability"], 
				face["rotation_angle"], face["yaw"],face["pitch"],face["roll"], 
				face["qualities"]["type"]["human"], face["qualities"]["type"]["cartoon"], id)
		else:

			updatesql = "UPDATE star_img SET ischeck = 1 WHERE id = '%d'" % (id)

		
		try:
			#print("updatesql="+updatesql)		
			# 执行SQL语句
			cursor.execute(updatesql)
		    # 提交到数据库执行
			db.commit()
		except:
		    # 发生错误时回滚
		    print("db udpate error")
		    db.rollback()

	return 1

####start###	
client =AipFace(APP_ID, API_KEY, SECRET_KEY)

#人脸检测中，在响应中附带额外的字段。年龄 / 性别 / 颜值 / 质量

options ={"face_fields":"age,gender,beauty,qualities"}

index = 1
while index == 1:

	
	index = aip_face_img(client, options)

	time.sleep(2)