#!/usr/bin/env python
#! --*-- coding: utf-8 --*--

import urllib
import logging
import datetime
import time 
import threading 
import Queue
import random
from BeautifulSoup import BeautifulSoup
import re
import copy
from pymongo import Connection
from pymongo.errors import ConnectionFailure
import json
import sys

from WeiboCrawler import WeiboCrawler

basepath = sys.argv[0]
if basepath.rfind("/") != -1:
	basepath = basepath[:basepath.rfind("/")]
else:
	basepath = "."

# logger setting
logger = logging.getLogger("Search")
logFileName = "%s/log/weibo/WeiboSearch.%s.log" % (basepath, str(datetime.date.today()))
fileHandler = logging.FileHandler(logFileName)
formatter = logging.Formatter("[%(asctime)s] [%(levelname)s] : %(message)s")
fileHandler.setFormatter(formatter)
logger.addHandler(fileHandler)
logger.setLevel(logging.INFO)

connect = Connection(host = "localhost", port = 27017)

class PersistJobs(threading.Thread):
	def __init__(self, results_queue):
		threading.Thread.__init__(self)
		self.dbh = connect['socialsearch']
		self.results_queue = results_queue
	
	def run(self):
		while True:
			result = self.results_queue.get()
			self.results_queue.task_done()
			self.dbh.users.insert(result, safe=True)

# prepare task based on the given keywords queue
class KeyWord(threading.Thread):
	def __init__(self, crawler, keywords, jobs):
		threading.Thread.__init__(self)
		self.crawler = crawler
		self.jobs = jobs
		self.keywords = keywords
		self.dbh = connect['keyword_date']
	
	def run(self):
		while True:
			if self.keywords.empty() == True:
				return
			
			# get a key word
			keyword, datestr = self.keywords.get()
			counter = 0
			limits = 2
			
			while True:
				time.sleep(5)
				#print "[%s][%s][%s]" % (counter, keyword, datestr)
				
				url = "http://weibo.cn/dpool/ttt/h5/hotword.php?isr=0&isp=0&stt=%s&ent=%s&act=advg&json=1&" % (datestr, datestr)
				referer = "http://weibo.cn/dpool/ttt/h5/hotword.php"
				params = urllib.urlencode({"keyword": keyword.strip()})
				url = url + params
				print url
				res = self.crawler.getPage(url, referer)
				print res
				
				if res is None:
					counter = counter + 1
					if counter > limits:
						break
					continue
				
				try:
					js = json.loads(res)
				except Exception, e:
					break
				
				if js['maxPage'] is None  or js['json'] is None:
					break
				
				maxPage = int(js['maxPage'])
				
				records = []
				for i in range(1, maxPage + 1):
					jobs.put((keyword, datestr, i))
					record = {
					    'keyword': keyword,
					    'datestr': datestr,
					    'page': i
					}
					records.append(record)
				
				self.dbh.jobs.insert(records)
				break
			
			self.keywords.task_done()

        
class Search(threading.Thread):
	def __init__(self, crawler, jobs, results_queue):
		threading.Thread.__init__(self)
		self.crawler = crawler
		self.jobs = jobs
		self.results_queue = results_queue
		self.dbh = connect['socialsearch']

	def run(self):
		users = []
		while True:
			if len(users) >= 100:
				self.results_queue.put(copy.deepcopy(users))
				del users[:]

			time.sleep(5)
			if self.jobs.empty() == True:
				if len(users) > 0:
					self.results_queue.put(copy.deepcopy(users))
					del users[:]
				return
			
			keyword, datestr, page = self.jobs.get()
			
			counter = 0
			limits = 2
			while True:
				url = "http://weibo.cn/dpool/ttt/h5/hotword.php?isr=0&isp=0&stt=%s&ent=%s&act=advg&json=1&page=%s&" % (datestr, datestr, page)
				referer = "http://weibo.cn/dpool/ttt/h5/hotword.php"
				params = urllib.urlencode({"keyword": keyword.strip()})
				url = url + params
				print url
				
				res = self.crawler.getPage(url, referer)
				with open("test_search.dat", "a") as sr:
					sr.write("%s\n" % res)

				if res is None:
					counter = counter + 1
					if counter > limits:
						break
					continue
				
				try:
					js = json.loads(res)
				except Exception, e:
					break
				
				if js['maxPage'] is None or js['json'] is None:
					break
				
				with open("baby_test_search.dat", "a") as ts:
					ts.write("%s\n" % res)

				data = js['json']
				for user in data:
					if isinstance(user, unicode):
						user = user.encode("utf-8")
					index = user.find("sina")
					uid = user[0 : index]
					uwid = user[index + 4 :]
					uwcont = data[user]['cont']
					uname = data[user]['info'][0]
					utime = data[user]['info'][1]
					ufrom = data[user]['info'][2]
					uzfs = data[user]['info'][3]
					upls = data[user]['info'][4]
					ugender = data[user]['gender']
					uvip = data[user]['vip']
					
					if isinstance(uwcont, unicode):
						uwcont = uwcont.encode("utf-8")
					if isinstance(uname, unicode):
						uname = uname.encode("utf-8")
					if isinstance(utime, unicode):
						utime = utime.encode("utf-8")
					if isinstance(ufrom, unicode):
						ufrom = ufrom.encode("utf-8")
					
					#print uid, wid, uname, utime, ufrom, ugender, uvip
					
					if 'zf' in data[user]:
						zfuser = data[user]['zf'][0]
						index = zfuser.find("sina")
						zfuid = zfuser[0 : index]
						zfwid = zfuser[index + 4 :]
						zfuname = data[user]['zf'][1][0]
						zfuvip = data[user]['zf'][1][1]
						if zfuvip != 0:
							zfuvip = 1
						zfwcont = data[user]['zf'][2]
						zfzfs = data[user]['zf'][3]
						zfpls = data[user]['zf'][4]
						
						if isinstance(zfuid, unicode):
							zfuid = zfuid.encode("utf-8")
						if isinstance(zfwid, unicode):
							zfwid = zfwid.encode("utf-8")
						if isinstance(zfuname, unicode):
							zfuname = zfuname.encode("utf-8")
						if isinstance(zfwcont, unicode):
							zfwcont = zfwcont.encode("utf-8")
						
						user_doc = {
						    "keyword": keyword,
						    "uid": uid,
							"uwid": uwid,
							"uwcont": uwcont,
						    "unick": uname,
						    "uvip": uvip,
						    "ugender": ugender,
						    "utime": utime,
						    "ufrom": ufrom,
							"uzfs": uzfs,
							"upls": upls,
						    "zfuid": zfuid,
						    "zfwid": zfwid,
						    "zfunick": zfuname,
						    "zfuvip": zfuvip,
						    "zfwcont": zfwcont,
						    "zfzfs": zfzfs,
						    "zfpls": zfpls
						}
						
#						users.append(user_doc)
					
					else:
						# construct a document
						
						user_doc = {
						    "keyword": keyword,
						    "uid": uid,
							"uwid": uwid,
							"uwcont": uwcont,
						    "unick": uname,
						    "uvip": uvip,
						    "ugender": ugender,
						    "utime": utime,
						    "ufrom": ufrom,
							"uzfs": uzfs,
							"upls": upls
						}
#						users.append(user_doc)

					with open("baby_search_result.dat", "a") as sr:
						sr.write("%s\n" % user_doc)
				break
	
			self.jobs.task_done()


if __name__ == "__main__":
	results_queue = Queue.Queue()
#	pj = PersistJobs(results_queue)
#	pj.setDaemon(True)
#	pj.start()

	crawler = WeiboCrawler()
	accounts_list = crawler.getAllGsidProxyPair()

	with open(sys.argv[1].strip()) as tasks:
		for task in tasks:
			if len(task.strip()) == 0:
				continue
			items = task.split("|")
			keyword = items[0].strip()
			year = int(items[1].strip())
			month = int(items[2].strip())
			day = int(items[3].strip())
			days = int(items[4].strip())
			keywords = Queue.Queue()
			jobs = Queue.Queue()
			start = datetime.date(year, month, day)
			print year, month, day
			
			#today = datetime.date.today()
			#start = datetime.date(2011, 9, 9)
			delta = datetime.timedelta(days = -1)
			date = start
			for i in range(days):
				datestr = date.strftime("%Y%m%d")
				#print datestr
				#print keyword
				keywords.put((keyword.strip(), datestr))
				date = date + delta
			
			objects = []
			for account in accounts_list:
				gsid = account[0]
				if account[1] == "None":
					proxy = None
				else: 
					proxy = account[1] 
				c = WeiboCrawler()
				c.setGsid(gsid)
				c.setProxy(proxy)
				objects.append(c)
				kw = KeyWord(c, keywords, jobs)
				kw.setDaemon(True)
				kw.start()
			
			keywords.join()
			
			for crawler in objects:
				s = Search(crawler, jobs, results_queue)
				s.setDaemon(True)
				s.start()
				
			jobs.join()
			logger.info("[%s] Done!" % task)
