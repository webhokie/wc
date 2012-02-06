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
import random
import time

from pymongo import ASCENDING
from pymongo import Connection
from pymongo.errors import ConnectionFailure

from WeiboCrawler import WeiboCrawler

basepath = sys.argv[0]
if basepath.rfind("/") != -1:
	basepath = basepath[:basepath.rfind("/")]
else:
	basepath = "."

# set up logger
logger = logging.getLogger("WeiboSocialGraph")
logFileName = basepath + "/log/weibo/WeiboSocialGraph." + str(datetime.date.today()) + ".log"
fileHandler = logging.FileHandler(logFileName)
formatter = logging.Formatter("[%(asctime)s] [%(levelname)s] : %(message)s")
fileHandler.setFormatter(formatter)
logger.addHandler(fileHandler)
logger.setLevel(logging.INFO)


runtime = int(time.time()) # figure out how to extract logs from log file.
logger.info("Program Time Signature: [%s]" % runtime)

class WeiboSocialGraph(threading.Thread):
	__DEBUG = True

	def __init__(self, jobs, crawler, dbh=None):
		threading.Thread.__init__(self)
		self.jobs = jobs
		#self.dbh = dbh
		self.crawler = crawler

	def run(self):
		while True:
			(uid, tp, page, number) = self.jobs.get()
			if number >= 3:
				self.jobs.task_done()
				continue

			if WeiboSocialGraph.__DEBUG:
				print (uid, tp, page)

			time.sleep(random.randint(2, 4))

			if tp == "att":
				res = self.crawler.getFriends(uid, page=page)
			else:
				res = self.crawler.getFans(uid, page=page)

			if res is None:
				logger.info("[uid:%s] [type:%s] [page:%s]" % (uid, tp, page))
				logger.error("response is None")
				number = number + 1
				self.jobs.put((uid, tp, page, number))
				self.jobs.task_done()
				continue

			try:
				js = json.loads(res) # convert to json format
			except Exception, e:
				logger.info("[uid:%s] [type:%s] [page:%s]" % (uid, tp, page))
				logger.info("response is: %s" % res)
				logger.error(e)

			 	print e
			 	print "social graph json.loads exception"
			 	print "response is %s" % res
			 	continue

			if js['ok'] == -100: # need relogin
			 	self.jobs.put((uid, tp, page, number))
				self.jobs.task_done()
			 	return

			if js['ok'] == 0: # no more pages
				self.jobs.task_done()
			 	continue

			if js['ok'] != 1: # unknown error 
				logger.info("[uid:%s] [type:%s] [page:%s]" % (uid, tp, page))
				logger.info("response is: %s" % res)
				logger.error("reponse ok is: %s" % js['ok'])
				logger.error("response msg is: %s" % js['msg'].encode("utf-8"))
			 	print js['ok']
			 	print js['msg'].encode("utf-8")
				self.jobs.task_done()
			 	continue

			# save into file
			with open("%s.%s" % (uid, tp), "a") as friends:
				friends.write("%s\n" % res)
			#try:
			#	data = js['data']
			#	peoples = []
			#	uidpairs = []
			#	for user in data:
			#	 	if isinstance(user, unicode):
			#			_uid = user.encode("utf-8")
			#		else:
			#			_uid = user
			#	 	
			#		uidpair = dict()
			#	 	if tp == "att": # user is uid's friends
			#	 		uidpair['srcid'] = uid # uid follows _u
			#			uidpair['destid'] = _uid
			#		if tp == "fans": # user is uid's fans
			#			uidpair['srcid'] = _uid # _u follows uid
			#			uidpair['destid'] = uid
			#		uidpairs.append(uidpair)

			#	 	people = dict()
			#		people['_id'] = _uid
			#		people['nick'] = data[user]['nick'].encode("utf-8")
			#		people['fans'] = data[user]['fans']
			#		if data[user]['vip'] == 0:
			#			people['vip'] = 0
			#		else:
			#			people['vip'] = 1
			#		people['ta'] = data[user]['ta'].encode("utf-8")
			#		people['vipReason'] = data[user]['vipReason'].encode("utf-8")
			#		people['description'] = data[user]['description'].encode("utf-8")
			#		people['location'] = data[user]['location'].encode("utf-8")
			#		people['checkFans'] = 0
			#		people['checkAtts'] = 0
			#		people['iTime'] = int(time.time())
			#		for key in people:
			#			print "[%s]%s" % (key, people[key])
			#		print "-------------------------"
			#		peoples.append(people)

			#	self.dbh.user.insert(peoples)
			#	self.dbh.graph.insert(uidpairs)
			#except Exception, e:
			#	print "analyize exception"
			#	print e
			#	logger.info("[uid:%s] [type:%s] [page:%s]" % (uid, tp, page))
			#	logger.info("response is: %s" % res)
			#	logger.error(e)
			#self.jobs.task_done()
			#break

class PrepareJobs(threading.Thread):
	def __init__(self, crawler, users, jobs, dbh=None):
		threading.Thread.__init__(self)
		self.users = users
		self.jobs = jobs
		self.dbh = dbh
		self.crawler = crawler

	def run(self):
		while True:
			time.sleep(random.randint(2, 4))
			uid, tp, number = self.users.get()
			if number >= 3:
				self.users.task_done()
				continue

			url = "http://m.weibo.cn/attention/getAttentionList?type=%s&uid=%s" % (tp, uid)
			print url

			if tp == "fans":
				res = self.crawler.getFans(uid)
			elif tp == "att":
				res = self.crawler.getFriends(uid)
			else:
				self.users.task_done()
				continue

			if res is None:
				logger.info(url)
				logger.error("response is None")
				number = number + 1
				self.users.put((uid, tp, number)) # put back
				self.users.task_done()
				print "[None]%s" % url
				continue
			try:
				js = json.loads(res)
			except Exception, e:
				logger.info(url)
				logger.info(res)
				logger.error(e)

				print "prepare fans jobs exception"
				print res
				print e
				number = number + 1
				self.users.put((uid, tp, number)) # put back
				self.users.task_done()
				continue

			ok = js['ok']
			if ok == 0: # success: no fans
				#self.dbh.user.update({"_id": uid}, {"$set": {"checkFans":1}}) 
				self.users.task_done()
				continue
			if ok == -100:
				self.users.put((uid, tp, number)) # put back
				self.users.task_done()
				return
			if ok != 1:
				self.users.put((uid, tp, number)) # put back
				self.users.task_done()
				logger.info(url)
				logger.info(res)
				logger.error("ok is %s" % ok)
				print "ok: %s" % ok
				continue

			maxPage = js['maxPage']
			if maxPage > 500:
				maxPage = 500
			for page in range(1, maxPage+1):
				self.jobs.put((uid, tp, page, 0))
			# update db
			#self.dbh.user.update({"_id": uid}, {"$set": {"checkFans":1}})
			self.users.task_done()


def main():
	try:
		connect = Connection(host="localhost", port=27017)
		print "Connected Successfully"
	except ConnectionFailure, e:
		sys.stderr.write("Could not connect to MongoDB: %s" % e)
		sys.exit(1)
	# Get a Database handle
	dbh = connect['weibo']

	users = Queue.Queue()
	jobs = Queue.Queue()
	users.put(("1646194541", "att", 0))
	

	wc = WeiboCrawler()
	accounts = wc.getAllGsidProxyPair()
	for account in accounts:
		gsid, proxy = account[0], account[1]
		if proxy == "None":
			proxy = None
		print gsid, proxy
		wct = WeiboCrawler(gsid=gsid, proxy=proxy)
		wct.setGsid(gsid)
		wct.setProxy(proxy)

		wsg = WeiboSocialGraph(jobs, wct)
		wsg.setDaemon(True)
		wsg.start()

		pj = PrepareJobs(wct, users, jobs)
		pj.setDaemon(True)
		pj.start()
		break

	time.sleep(4000)

#	while True:
#		users = dbh.user.find({"checkAtts":0}, {"_id":1}, limit=10, sort=[("iTime", ASCENDING)])
##		users = dbh.user.find({"checkFans":0, "checkAtts":0, "fans":{"$lte": 5000}}, {"_id":1}, limit=10, sort=[("iTime", ASCENDING)])
#		for user in users:
#			print user['_id']
#			logger.info("[job][%s]" % user['_id'])
#			atts.put(user['_id'])
#
#		while True:
#			print "jobs: %s" % jobs.qsize()
#			if jobs.empty() == True and fans.empty() == True and atts.empty() == True:
#				break
#			time.sleep(30)
#	print "done"

if __name__ == "__main__":
	main()
	logger.info("Program Time Signature: [%s]" % runtime)
