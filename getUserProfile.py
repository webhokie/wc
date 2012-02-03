#!/usr/bin/env python
# -*- coding: utf-8 -*-

# @Author (Junwei)
# @Date (2012-02-03)

import sys
import time
import json
import Queue
import datetime
import threading

from WeiboCrawler import WeiboCrawler

basepath = sys.argv[0]
if basepath.rfind("/") != -1:
	basepath = basepath[:basepath.rfind("/")]
else:
	basepath = "."

class GetProfile(threading.Thread):
	def __init__(self, crawler, jobs_queue):
		threading.Thread.__init__(self)
		self.crawler = crawler
		self.jobs_queue = jobs_queue

	def run(self):
		while True:
			if self.jobs_queue.empty():
				return
			uid, number = self.jobs_queue.get()
			if number >= 3:
				continue
			url = "http://m.weibo.cn/users/getUserAllInfo?uid=%s" % uid
			referer = "http://m.weibo.cn/users/%s?" % uid

			res = self.crawler.getPage(url, referer)
			if res is None:
				number = number + 1
				self.jobs_queue.put((uid, number))
				self.jobs_queue.task_done()
				continue
			try:
				js = json.loads(res)
				if int(js['ok']) == 1:
					with open("%s/data/profile/%s.info" % (basepath, datetime.date.today()), "a") as profilef:
						profilef.write("%s\n" % res)
					self.jobs_queue.task_done()
				else:
					raise Exception("Unknown Excpetion")
			except Exception, e:
				logger.info(url)
				logger.info(res)
				logger.error(e)
				number = number + 1
				self.jobs_queue.put((uid, number))
				self.jobs_queue.task_done()
				continue

if __name__ == "__main__":
	jobs_queue = Queue.Queue()
	jobs_queue.put(("1804147667", 0))
	wc = WeiboCrawler()
	accounts = wc.getAllGsidProxyPair()
	gsid, proxy = accounts[0]
	if proxy == "None":
		proxy = None
	print gsid, proxy
	wc.setGsid(gsid)
	wc.setProxy(proxy)
	gp = GetProfile(wc, jobs_queue)
	gp.setDaemon(False)
	gp.start()
