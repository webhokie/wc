#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Date (2012-01-13)
# Author (Junwei)

import re
import os
import sys
import time
import socket
import logging
import datetime
import traceback
import cookielib
import mechanize
from urllib2 import HTTPError
from BeautifulSoup import BeautifulSoup

# global tcp timeout setting
socket.setdefaulttimeout(5)

basepath = sys.argv[0]
if basepath.rfind("/") != -1:
	basepath = basepath[:basepath.rfind("/")]
else:
	basepath = "."

# logger
_logger = logging.getLogger("BaseCrawler")
logFile = "%s/log/weibo/BaseCrawler.%s.log" % (basepath, str(datetime.date.today()))
logHandler = logging.FileHandler(logFile)
logFormatter = logging.Formatter("[%(asctime)s] [%(levelname)s] : %(message)s")
logHandler.setFormatter(logFormatter)
_logger.addHandler(logHandler)
_logger.setLevel(logging.INFO)


# Use Defined Exception
class CrawlerException(Exception):
	def __init__(self, msg):
		self.msg = msg
	def __str__(self):
		return repr(self.msg)

class BaseCrawler(object):
	def createBrowser(self, mode=False):
		"""
		mode = True if in debug mode
		mode = False if in productive mode
		"""
		br = mechanize.Browser(factory = mechanize.RobustFactory())
		br.set_handle_equiv(True)
		br.set_handle_redirect(True)
		br.set_handle_referer(True)
		br.set_handle_robots(False)
		br.set_handle_refresh(mechanize._http.HTTPRefreshProcessor(), max_time=1)
		br.set_debug_http(mode)
		br.set_debug_responses(mode)
		br.set_debug_redirects(mode)
		br.addheaders = [("User-Agent", "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.7 (KHTML, like Gecko) C    hrome/16.0.912.63 Safari/535.7")]
		cj = cookielib.LWPCookieJar()
		br.set_cookiejar(cj)
		return br

	def __init__(self, logger=None, username=None, password=None, proxy=None):
		# logger setting
		if logger is None:
			self.logger = _logger
		else:
			self.logger = logger
		
		# account setting
		self.proxy = proxy
		self.username = username
		self.password = password
		self.is_login = False

		# browser
		self.br = mechanize.Browser(factory = mechanize.RobustFactory())
		self.br.set_handle_equiv(True)
		self.br.set_handle_redirect(True)
		self.br.set_handle_referer(True)
		self.br.set_handle_robots(False)
		self.br.set_handle_refresh(mechanize._http.HTTPRefreshProcessor(), max_time = 1)
		self.br.set_debug_http(True)
		self.br.set_debug_responses(True)
		self.br.set_debug_redirects(True)

		self.br.addheaders = [
							 	("User-Agent", "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.7 (KHTML, like Gecko) Chrome/16.0.912.63 Safari/535.7")
							 ]

		# cookiejar
		self.cj = cookielib.LWPCookieJar()
		self.br.set_cookiejar(self.cj)

		# login status
		self.is_login = False


	def getPage(self, url, referer=None):
		req = mechanize.Request(url)
		if referer is not None:
			req.add_header("Referer", referer)

		try:
			resp = self.br.open(req).read()
		except Exception, e:
			self.logger.error("url:%s, msg:%s" % (url, e))
			traceback.print_exc(file=sys.stderr)
			resp = None
		return resp
	
	def setProxy(self, proxy):
		if proxy is not None:
			self.proxy = proxy
			self.br.set_proxies({"http": proxy})
	

	def setUserName(self, username):
		if username is not None:
			self.username = username

	def setPassword(self, password):
		if password is not None:
			self.password = password

	def setDefaultTimeout(seconds):
		try:
			seconds = int(seconds)
		except Exception, e:
			seconds = None
			
		if seconds is None or seconds <= 0:
			seconds = 5

		socket.setdefaulttimeout(seconds)

if __name__ == "__main__":
	#crawler = BaseCrawler()
	##resp = crawler.getPage("http://beijing.douban.com/events/future/all?start=0")
	#resp = crawler.getPage("http://jijiwaiwai.jiji")
	#print resp
	pass
