#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import logging
import datetime
import time
import MySQLdb
import Queue
import threading
import sys
import random

from WeiboCrawler import WeiboCrawler

basepath = sys.argv[0]
if basepath.rfind("/") != -1:
	basepath = basepath[:basepath.rfind("/")]
else:
	basepath = "."

# from retweet relationship
logger = logging.getLogger("getUserFansByRepost")
logFileName = basepath + "/log/weibo/WeiboFansRepost." + str(datetime.date.today()) + ".log"
fileHandler = logging.FileHandler(logFileName)
formatter = logging.Formatter("[%(asctime)s] [%(levelname)s] : %(message)s")
fileHandler.setFormatter(formatter)
logger.addHandler(fileHandler)
logger.setLevel(logging.INFO)


class FansByRepost(threading.Thread):
    def __init__(self, crawler, jobs_queue):
        threading.Thread.__init__(self)
        self.crawler = crawler
        self.jobs_queue = jobs_queue
        print self.jobs_queue.qsize()

    def run(self):
        while True:
            if self.jobs_queue.empty() == True:
                return
            uid, page, number = self.jobs_queue.get()
            self.jobs_queue.task_done()
            if number >= 3: # fail number
            	continue
            
            time.sleep(2)
            url = "http://weibo.cn/dpool/ttt/h5/msg.php?cat=4&json=1&uid=%s&page=%s" % (uid, page)
            referer = "http://weibo.cn/"
            
            print "[-%s]%s" % (number, url)
            
            res = self.crawler.getPage(url, referer)
            print res
            
            if res is None:
            	number = number + 1
            	self.jobs_queue.put((uid, page, number))
            	continue
            
            try:
                js = json.loads(res)
            except Exception, e:
            	logger.info(url)
            	logger.info(res)
            	logger.error(e)
            	number = number + 1
            	self.jobs_queue.put((uid, page, number))
                continue
            
            if js['maxPage'] is None or js['json'] is None:
                continue
            
            with open("%s/data/repost/%s.repost" % (basepath, datetime.date.today()), "a") as repostf:
            	repostf.write("%s\n" % res)

class InitJobQueue(threading.Thread):
    def __init__(self, crawler, uid_queue, jobs_queue):
        threading.Thread.__init__(self)
        self.crawler = crawler
        self.uid_queue = uid_queue
        self.jobs_queue = jobs_queue

    def run(self):
        while True:
            if self.uid_queue.empty() == True:
                return
            
            uid, number = self.uid_queue.get()
            if number >=3:
            	self.uid_queue.task_done()
                continue
            
            time.sleep(2)
            url = "http://weibo.cn/dpool/ttt/h5/msg.php?cat=4&json=1&uid=%s&page=1" % uid
            referer = "http://weibo.cn"
            print "[%s]%s" % (number, url)
            res = self.crawler.getPage(url, referer)
            #print res
            
            if res is None:
                number = number + 1
                self.uid_queue.put((uid, number))
            	self.uid_queue.task_done()
                continue
            
            try:
                js = json.loads(res)
            except Exception, e:
                number = number + 1
                self.uid_queue.put((uid, number))
            	self.uid_queue.task_done()
                logger.info(url)
                logger.info(res)
                logger.error(e)
                continue
            
            if js['maxPage'] is None:
                logger.info(url)
                logger.info(res)
                logger.error("max page is none")
                continue
            
            maxPage = js['maxPage']
            print "max page:", maxPage
            for i in range(1, maxPage + 1):
                self.jobs_queue.put((uid, i, 0))
            self.uid_queue.task_done()





if __name__ == "__main__":
    uid_queue = Queue.Queue()
    jobs_queue = Queue.Queue()
    
    uid_queue.put(("1647717847", 0)) # test
    
    crawler = WeiboCrawler()
    accounts = crawler.getAllGsidProxyPair()
    
    account_list = []
    for account in accounts:
        gsid, proxy = account[0], account[1]
        if proxy == "None":
        	proxy = None
        c = WeiboCrawler()
        c.setGsid(gsid)
        c.setProxy(proxy)
        ijq = InitJobQueue(c, uid_queue, jobs_queue)
        ijq.setDaemon(True)
        ijq.start()
        account_list.append(c)
        
	uid_queue.join()
	
    for c in account_list:
        fbr = FansByRepost(c, jobs_queue)
        fbr.setDaemon(True)
        fbr.start()
    
    jobs_queue.join()	
    time.sleep(30)
