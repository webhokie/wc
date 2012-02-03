#!/usr/bin/env python2.7
#! -*- coding: utf-8 -*-

# Date (2012-01-31)
# Author (Junwei)

import json
import logging
import datetime
import threading
import Queue
import sys
import re
import random
import time

from BeautifulSoup import BeautifulSoup
from pymongo import ASCENDING
from pymongo import Connection
from pymongo.errors import ConnectionFailure

from WeiboCrawler import WeiboCrawler

basepath = sys.argv[0]
if basepath.find("/") != -1:
	basepath = basepath[:basepath.find("/")]
else:
	basepath = "."

# set up logger
logger = logging.getLogger("WeiboGetLatestBlog")
logFileName = basepath + "/log/weibo/WeiboGetLatestBlog." + str(datetime.date.today()) + ".log"
fileHandler = logging.FileHandler(logFileName)
formatter = logging.Formatter("[%(asctime)s] [%(levelname)s] : %(message)s")
fileHandler.setFormatter(formatter)
logger.addHandler(fileHandler)
logger.setLevel(logging.INFO)


runtime = int(time.time()) # figure out how to extract logs from log file.
logger.info("Program Time Signature: [%s]" % runtime)

class DataManager(threading.Thread):
	""" Store Data Into Database """
	# @Param database name
	# @Param collection name
	# @Param task queue
	def __init__(self, dname, cname, results_queue):
		threading.Thread.__init__(self)
		self.database = dname
		self.collection = cname
		self.results_queue = results_queue
		self.dbh = connect[self.database]
	def run(self):
		data = []
		while True:
			item = self.results_queue.get()
			data.append(item)
			if len(data) >= 10:
				self.dbh[self.collection].insert(data)
				del data[:]

class WeiboException(Exception):
	def __init__(self, code, message):
		self.code = code
		self.message = message

	def __str__(self):
		return repr(self.message)

class GetLatestBlog(threading.Thread):
	def __init__(self, jobs_queue, results_queue, gsid, proxy=None):
		threading.Thread.__init__(self)
		self.jobs_queue = jobs_queue
		self.results_queue = results_queue
		self.gsid = gsid
		self.proxy = proxy
		self.wc = WeiboCrawler()
		self.wc.setGsid(self.gsid)
		self.wc.setProxy(self.proxy)

	def run(self):
		while True:
			time.sleep(random.randint(2, 4))

			uid, page = self.jobs_queue.get()
			self.jobs_queue.task_done()

			if page is None:
				page = "1"
			resp = self.wc.getMicroBlogs(uid, page)
			if resp is None:
				self.jobs_queue.put(uid)
			soup = BeautifulSoup(resp)
			body = soup.body
			mblogs = body.findAll("div", {"class": "c", "id": re.compile(u"M_")})
			if mblogs is None: # no micro blog
				continue
			#print mblogs
			blogs_file = open("%s/data/blogs/%s.blog" % (basepath, datetime.date.today()), "a")
			for mblog in mblogs:
				blogs_file.write("[%s]:%s\n" % (uid, mblog))
			blogs_file.close()
				
			
def main():
	results_queue = Queue.Queue()
	jobs_queue = Queue.Queue()

	wc = WeiboCrawler()
	accounts = wc.getAllGsidProxyPair()

	gsid, proxy = accounts[0][0], accounts[0][1]
	if proxy == "None":
		proxy = None
	wc.setGsid(gsid)
	wc.setProxy(proxy)

	res = wc.getMicroBlogs("1646194541")
	soup = BeautifulSoup(res)
	pagelist = soup.find("div", {"id": "pagelist"})
	mp = pagelist.find("input", {"name": "mp"})

	uid = "xxxxxxxxx"
	for page in range(1, int(mp) + 1):
		jobs_queue.put((uid, page))
	for account in accounts:
		gsid = account[0]
		proxy = account[1]
		if proxy == "None":
			proxy = None
		glb = GetLatestBlog(jobs_queue, results_queue, gsid, proxy)
		glb.setDaemon(True)
		glb.start()

	jobs_queue.join()

if __name__ == "__main__":
	main()
	logger.info("Program Time Signature: [%s]" % runtime)
