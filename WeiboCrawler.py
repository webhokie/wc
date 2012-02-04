#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Date (2012-01-13)
# Author (Junwei)

import logging
import datetime
import cookielib
import os
import re
import sys
import mechanize
import traceback

from BeautifulSoup import BeautifulSoup
from BaseCrawler import BaseCrawler
import CodeChecker

basepath = sys.argv[0]
if basepath.rfind("/") != -1:
	basepath = basepath[:basepath.rfind("/")]
else:
	basepath = "."


# logger
logger = logging.getLogger("WeiboCrawler")
logFile = "%s/log/weibo/WeiboCrawler.%s.log" % (basepath, str(datetime.date.today()))
logHandler = logging.FileHandler(logFile)
logFormatter = logging.Formatter("[%(asctime)s] [%(levelname)s] : %(message)s")
logHandler.setFormatter(logFormatter)
logger.addHandler(logHandler)
logger.setLevel(logging.INFO)


class WeiboCrawler(BaseCrawler):
	def __init__(self, logger=None, username=None, password=None, proxy=None, gsid=None):
		if gsid is not None:
			self.gsid = gsid
			self.is_login = True
		else:
		 	self.gsid = None
		 	self.is_login = False
		super(WeiboCrawler, self).__init__(logger, username, password, proxy)

	def setDomain(self, domain):
		if domain is None:
			return
		if not self.is_login:
			return

		url = "http://weibo.cn/account/setting/domain/"
		referer = "http://weibo.cn/account/setting/domain/"
		resp = self.getPage(url, referer)
		if resp is None:
			return

		# select domain form
		self.br.select_form(nr=0)
		#print self.br.form

		# set domain
		try:
			self.br.form['domain'] = domain.strip()
			print self.br.form['domain']
		except Exception, e: # no control matching name domain: already set
			print e
			return
			
		# submit
		#self.br.submit()
		_resp = self.br.submit()
		print _resp.info()
		resp_url =  _resp.geturl()
		if resp_url.find("http://weibo.cn/account/setting/domain") != -1:
			# invalid domain
			guess = domain + "a"
			if len(guess) >= 20:
				return
			self.setDomain(guess)

	def setDescription(self, description):
		if description is None:
			return
		if not self.is_login:
			return
		url = "http://weibo.cn/account/setting/intro/"
		referer = "http://weibo.cn/account/setting/intro/"
		resp = self.getPage(url, referer)
		if resp is None:
			return

		# select description form
		self.br.select_form(nr=0)
		# print self.br.form

		# show old description
		print "old description is:", self.br.form['intro']

		# set new description
		self.br.form['intro'] = description.strip()

		self.br.submit()

	def setTag(self, tag):
		if tag is None:
			return
		if not self.is_login:
			return
		url = "http://weibo.cn/account/privacy/tags/"
		referer = "http://weibo.cn/account/privacy/tags/"
		resp = self.getPage(url, referer)
		if resp is None:
			return

		# select description form
		self.br.select_form(nr=0)
		# print self.br.form

		# add new tag
		self.br.form['tag'] = tag.strip()

		self.br.submit()

	def setLocation(self, provid=None, cityid=None):
		if not self.is_login:
			return
		if provid is None or cityid is None:
			provid = "11"
			cityid = "1"

		url = "http://weibo.cn/account/privacy/city/?provid=%s&cityid=%s" % (provid, cityid)
		referer = "http://weibo.cn/account/privacy/city/"
		resp = self.getPage(url, referer)

	def setGender(self, gender):
		if gender is None:
			return
		if not self.is_login:
			return

		url = "http://weibo.cn/account/setting/gender/"
		referer = "http://weibo.cn/account/setting/gender/"
		resp = self.getPage(url, referer)
		if resp is None:
			return

		# select description form
		self.br.select_form(nr=0)
		# print self.br.form

		# select gender
		if gender == 'f':
			self.br.form['gender'] = ['f'] # or self.br.set_value(['f'], name='gender')
		else:
			self.br.form['gender'] = ['m']
		self.br.submit()

	def setSchool(self, schoolid, year, department=None): 
		if schoolid is None or year is None:
			return
		if not self.is_login:
			return

		url = "http://weibo.cn/account/school/addschool/?school_id=%s" % schoolid
		referer = "http://weibo.cn/account/"
		resp = self.getPage(url, referer)
		if resp is None:
			return

		# select description form
		self.br.select_form(nr=0)
		# print self.br.form

		# set year
		self.br.form['year'] = year.strip()
		if department is not None:
			self.br.form['department'] = department.strip()
		self.br.submit()

	def setCompany(self, company_name, in_year=None, out_year=None, department=None): 
		if company_name is None:
			return
		if not self.is_login:
			return

		url = "http://weibo.cn/account/company/add"
		referer = "http://weibo.cn/account/"
		resp = self.getPage(url, referer)
		if resp is None:
			return

		# select description form
		self.br.select_form(nr=0)
		# print self.br.form

		# set company info
		self.br.form['company'] = company_name.strip()
		if in_year is not None:
			self.br.form['start'] = in_year.strip()
		if out_year is not None:
			self.br.form['end'] = out_year.strip()
		if department is not None:
			self.br.form['department'] = department.strip()
		self.br.submit()


	def setAvatar(self, path, mime, name):
		if path is None or mime is None or name is None:
			return
		if not self.is_login:
			return

		url = "http://weibo.cn/account/setting/avatar/"
		referer = "http://weibo.cn/account/setting/avatar/"

		resp = self.getPage(url, referer)
		if resp is None:
			return

		self.br.select_form(nr=0)
		print self.br.form

		self.br.form.add_file(open(path), mime, name)
		self.br.submit()


	def setBirthday(self, year, month, day): 
		if year is None or month is None or day is None:
			return
		if not self.is_login:
			return

		url = "http://weibo.cn/account/setting/birth/"
		referer = "http://weibo.cn/account/setting/birth/"
		resp = self.getPage(url, referer)
		if resp is None:
			return

		# select birth form
		self.br.select_form(nr=0)
		print self.br.form

		# set birth info
		self.br.form['year'] = year.strip()
		self.br.form['month'] = month.strip()
		self.br.form['day'] = day.strip()

		self.br.submit()
		#print self.br.submit().read()

	def sendBlog(self, content, **kwds):
		if content is None:
			return
		if not self.is_login:
			return

		url = "http://weibo.cn/mblog/sendmblog?composer=1"
		referer = "http://weibo.cn/"
		resp = self.getPage(url, referer)
		if resp is None:
			return

		self.br.select_form(nr=0)
		print self.br.form

		# set content
		self.br.form['content'] = content.strip()

		have_pic = False
		for key in kwds:
			have_pic = True
			if key == "path":
				path = kwds[key]
			if key == "mime":
				mime = kwds[key]
			if key == "name":
				name = kwds[key]
		if have_pic:
			self.br.form.add_file(open(path), mime, name)

		self.br.submit()

	def repost(self, mid, content=None):
		if mid is None:
			return 
		if not self.is_login:
			return

		url = "http://weibo.cn/repost/%s?rl=0" % mid
		referer = "http://weibo.cn"
		resp = self.getPage(url, referer)
		if resp is None:
			return

		self.br.select_form(nr=0)
		print self.br.form

		if content is not None:
			self.br.form['content'] = content.strip()

		self.br.submit()

	def comment(self, mid, content):
		if mid is None or content is None:
			return 
		if not self.is_login:
			return

		url = "http://weibo.cn/comment/%s?rl=0" % mid
		referer = "http://weibo.cn"
		resp = self.getPage(url, referer)
		if resp is None:
			return

		try:
			self.br.select_form(nr=0)
			#print self.br.form
			self.br.form['content'] = content.strip()
			_resp = self.br.submit()
			resp_url =  _resp.geturl()
			#print _resp.read()
			if resp_url.find("http://weibo.cn/comments/addcomment") != -1:
				logger.info(_resp.read())
				raise Exception("permission denied")
			return True
		except Exception, e:
			logger.info(url)
			logger.error(e)
			return False

	def setNick(self, nick):
		if nick is None:
			return
		if not self.is_login:
			return
		url = "http://weibo.cn/account/setting/nick/"
		referer = "http://weibo.cn/account/setting/nick"
		resp = self.getPage(url, referer)
		if resp is None:
			return

		# select nick form
		self.br.select_form(nr=0)
		# print self.br.form

		# show old nick
		print "old nick is:", self.br.form['nick']

		# set new nick
		self.br.form['nick'] = nick.strip()

		# submit this form
		#self.br.submit()
		_resp = self.br.submit()
		print _resp.info()
		resp_url =  _resp.geturl()
		if resp_url.find("setting") != -1:
			soup = BeautifulSoup(_resp.read())
			a = soup.find("a", {"href": re.compile(u"^/account/setting/nick/\?save=1&changenicktomblog=1&nick=")})
			while a.string.strip() == "":
				a = soup.find("a", {"href": re.compile(u"^/account/setting/nick/\?save=1&changenicktomblog=1&nick=")})
				
			tip = a.string.strip().encode("utf-8")
			self.setNick(tip)
		#resp = _resp.read()
		#print resp




	def getFriends(self, uid, page=None, referer=None):
		if referer is None:
			referer = "m.weibo.cn"
		url = "http://m.weibo.cn/attention/getAttentionList?type=att&uid=%s" % uid
		if page is not None:
			url = "%s&page=%s" % (url, page)
		return self.getPage(url, referer=referer) 

	def getFans(self, uid, page=None, referer=None):
		if referer is None:
			referer = "m.weibo.cn"
		url = "http://m.weibo.cn/attention/getAttentionList?type=fans&uid=%s" % uid
		if page is not None:
			url = "%s&page=%s" % (url, page)
		return self.getPage(url, referer=referer) 

	def getMicroBlogs(self, uid, page="1", filter="1"):
		"""filter=0 => all microblogs, filter=1 => original"""
		if uid is None:
			return
		if not self.is_login:
			return
		url = "http://weibo.cn/%s/profile?filter=%s&page=%s" % (uid, filter, page)
		referer = "http://weibo.cn/%s/profile" % uid
		return self.getPage(url, referer=referer)
		
	def attention(self, uid):
		if uid is None:
			return
		if not self.is_login:
			return

		url = "http://weibo.cn/attention/add/%s?rl=0" % uid
		referer = "http://weibo.cn"

		self.getPage(url, referer)

	def setGsid(self, gsid):
		if gsid is not None:
			self.gsid = gsid
			self.is_login = True

	def getPage(self, url, referer=None):
		if self.is_login:
			if url.rfind("?") == -1:
				url = "%s?&gsid=%s" % (url, self.gsid)
				print url
			else:
				url = "%s&gsid=%s" % (url, self.gsid)
		return super(WeiboCrawler, self).getPage(url, referer)	

	def getAllGsidProxyPair(self):
		(root, dirs, files) = os.walk('%s/accounts' % basepath).next()
		data = []
		for f in files:
			if f.endswith("cookie"):
				cj = cookielib.LWPCookieJar()
				cj.load("%s/accounts/%s" % (basepath, f))
				cookies = [cookie for cookie in cj if cookie.domain == ".sina.cn"] # get sina.cn cookie if valid
				if len(cookies) == 0: # expired cookie
					os.rename("%s/accounts/%s" % (basepath, f), "%s/accounts/%s.invalid" % (basepath, f))
				else:
					cookie = cookies[0]
					gsid_proxy_pair = "%s/accounts/%s" % (basepath, f.replace("cookie", "gp"))
					with open(gsid_proxy_pair, "r") as gsid_proxy:
						gsid, proxy = gsid_proxy.readline().strip().split()
						if proxy.startswith("None"):
							proxy = None
						data.append((gsid, proxy))
		return data
		

	def login(self, username=None, password=None, proxy=None):
		if proxy is not None:
			super(WeiboCrawler, self).setProxy(proxy)

		if self.is_login or username is None or password is None:
			return

		super(WeiboCrawler, self).setUserName(username)
		super(WeiboCrawler, self).setPassword(password)

		# login
		url = "http://3g.sina.com.cn/prog/wapsite/sso/login.php"
		referer = "http://weibo.cn/dpool/ttt/home.php"
		resp = self.getPage(url, referer)
		if resp is None:
			logger.error("%s, %s, %s, response is None" % (self.username, self.password, self.proxy))
			return

		# select the first form
		try:
			self.br.select_form(nr=0)
		except Exception, e:
			logger.error("%s, %s, %s, %s" % (self.username, self.password, self.proxy, e))
			return

		# check what fields there might be: cause sina's from has a variable form name of password
		for control in self.br.form.controls:
			if control.name is None:
				continue
			if control.name.find("mobile") != -1:
				self.br.form[control.name] = self.username
			if control.name.find("password") != -1:
				self.br.form[control.name] = self.password

		# submit this form
		_resp = self.br.submit()
		print _resp.info()
		print _resp.geturl()
		resp = _resp.read()
		print resp
		if resp is None:
			logger.error("%s, %s, %s, response is None" % (self.username, self.password, self.proxy))
			return 
		soup = BeautifulSoup(resp)
		error_msg = soup.find("div", {"class": "msgErr"})
		if error_msg is None:
			try:
				cookie_file = "%s/accounts/%s.weibo.cookie" % (basepath, self.username)
				gsid_proxy_file = "%s/accounts/%s.weibo.gp" % (basepath, self.username) # suffix gp means g[gsid] and p[proxy] pair
				if os.path.isfile(cookie_file):
					os.remove(cookie_file)
				self.cj.save(cookie_file)
				cookie = [cookie for cookie in self.cj if cookie.domain == ".sina.cn"][0]
				self.gsid = cookie.value
				self.is_login = True
				with open(gsid_proxy_file, "w") as gsid_proxy_pair:
					gsid_proxy_pair.write("%s\t%s\n" % (self.gsid, self.proxy))
			except Exception, e:
			  	logger.error("%s, %s, %s, %s" % (self.username, self.password, self.proxy, e))
				print self.username, self.password, self.proxy, e
		else:
			try:
				msg = error_msg.string
				if isinstance(msg, unicode):
					msg = msg.encode("utf-8")
				if msg == "请输入验证码":
					img = soup.find("img", {"alt": re.compile(u"请打开图片显示")})	
					if img is None:
						return
					img_url = img['src']
					print img_url
					browser =  mechanize.Browser(factory = mechanize.RobustFactory())
					browser.set_handle_robots(False)
					browser.addheaders = [("User-Agent", "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.7 (KHTML, like Gecko) Chrome/16.0.912.63 Safari/535.7")]
					browser.set_cookiejar(self.cj)
					req = mechanize.Request(img_url)
					response = browser.open(req).read()
					open("show.gif", "w").write(response)
					checker = CodeChecker.App("show.gif")
					print checker.code
			except Exception, e:
				traceback.print_exc()
				print sys.exc_info()
				print e


	def showCurDir(self):
		print sys.argv[0]
		
if __name__ == "__main__":
#	with open("%s/collection/acct.t" % basepath, "r") as accounts:
#		for account in accounts:
#			items = account.strip().split("|")
#			username = items[0]
#			password = items[1]
#			proxy = items[2]
#			wc = WeiboCrawler()
#			wc.login(username, password, proxy)


	wc = WeiboCrawler()
	wc.login("1183964328@qq.com", "a666666")
#	gsid_proxy_pairs = wc.getAllGsidProxyPair()
	#print gsid_proxy_pairs
#	gsid, proxy = gsid_proxy_pairs[4]
	#print gsid
#	wc.setGsid(gsid)
#	print wc.getMicroBlogs("1682352065")
#	wc.setNick("福气鱼")
#	wc.setNick("福气鱼01101")
#	wc.setDomain("bestofme")
#	wc.setDescription("这是我的自我描述")
#	wc.setTag("吃,喝,玩,乐")
#	wc.setGender("m")
#	wc.setLocation("11", "2")
#	wc.setSchool("243972", "2006", "中国传媒大学简介")
#	wc.setCompany("2688", "2006", department="中国传媒大学简介")
#	wc.setBirthday("1994", "3", "27") 
#	wc.setAvatar("a", "3", "27") 
#	wc.sendBlog("send a picture", path="0UI51A3-0-lp.jpg", mime="image/jpeg", name="OUI51A3-0-lp.jpg")
#	wc.sendBlog("send a picture")
#	wc.repost("y3sT3xCZP", "悲剧")
#	print wc.comment("y3sT3xCZP", "悲剧")
#	print wc.comment("y3MAYnnqf", "悲剧")
#	wc.attention("2571243662")
#	resp = wc.getFans(2338835395)
#	resp = wc.getPage("http://weibo.cn/2097199585/follow", referer="http://weibo.cn/u/20978199585")
#	resp = wc.getPage("http://weibo.cn/?vt=4", referer="www.baidu.com")
#	print resp
