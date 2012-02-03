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
# weibo.cn/dpool/ttt/h5/attension.php?cat=1&uid=%s&json=1
logger = logging.getLogger("getUserFansByCmtCn")
logFileName = basepath + "/log/weibo/WeiboFansCmtCn." + str(datetime.date.today()) + ".log"
fileHandler = logging.FileHandler(logFileName)
formatter = logging.Formatter("[%(asctime)s] [%(levelname)s] : %(message)s")
fileHandler.setFormatter(formatter)
logger.addHandler(fileHandler)
logger.setLevel(logging.INFO)


class FansByCmt(threading.Thread):
    def __init__(self, crawler, jobs_queue):
        threading.Thread.__init__(self)
        self.crawler = crawler
        self.jobs_queue = jobs_queue
        print self.jobs_queue.qsize()

    def run(self):
        while True:
            if self.jobs_queue.empty() == True:
                return
            mid, page, number = self.jobs_queue.get()
            self.jobs_queue.task_done()
            if number >= 3: # fail number
            	continue
            
            time.sleep(2)
            url = "http://weibo.cn/dpool/ttt/h5/comment.php?json=1&srcid=%s&page=%s" % (mid, page)
            referer = "http://weibo.cn/"
            
            print "[-%s]%s" % (number, url)
            
            res = self.crawler.getPage(url, referer)
            print res
            
            if res is None:
            	number = number + 1
            	self.jobs_queue.put((mid, page, number))
            	continue
            
            try:
                js = json.loads(res)
            except Exception, e:
            	logger.info(url)
            	logger.info(resp)
            	logger.error(e)
            	number = number + 1
            	self.jobs_queue.put((mid, page, number))
                continue
            
            if js['maxPage'] is None or js['json'] is None:
                continue
            
            with open("%s/data/comments/%s.cmt" % (basepath, datetime.date.today()), "a") as commentf:
            	commentf.write("%s\n" % res)

class InitJobQueue(threading.Thread):
    def __init__(self, crawler, mid_queue, jobs_queue):
        threading.Thread.__init__(self)
        self.crawler = crawler
        self.mid_queue = mid_queue
        self.jobs_queue = jobs_queue

    def run(self):
        while True:
            if self.mid_queue.empty() == True:
                return
            
            mid, number = self.mid_queue.get()
            if number >=3:
            	self.mid_queue.task_done()
                continue
            
            time.sleep(2)
            url = "http://weibo.cn/dpool/ttt/h5/comment.php?json=1&srcid=%s&page=1" % mid
            referer = "http://weibo.cn"
            print "[%s]%s" % (number, url)
            res = self.crawler.getPage(url, referer)
            #print res
            
            if res is None:
                number = number + 1
                self.mid_queue.put((mid, number))
            	self.mid_queue.task_done()
                continue
            
            try:
                js = json.loads(res)
            except Exception, e:
                number = number + 1
                self.mid_queue.put((mid, number))
            	self.mid_queue.task_done()
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
                self.jobs_queue.put((mid, i, 0))
            self.mid_queue.task_done()





if __name__ == "__main__":
    mid_queue = Queue.Queue()
    jobs_queue = Queue.Queue()
    
    mid_queue.put(("y3FIBFbE0", 0)) # test
    
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
        ijq = InitJobQueue(c, mid_queue, jobs_queue)
        ijq.setDaemon(True)
        ijq.start()
        account_list.append(c)
        
	mid_queue.join()
	
    for c in account_list:
        fbc = FansByCmt(c, jobs_queue)
        fbc.setDaemon(True)
        fbc.start()
    
    jobs_queue.join()	
    time.sleep(30)
