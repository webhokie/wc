#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Date (2012-02-01)
# Author (Junwei)

import sys
import Queue
import fileinput

from WeiboCrawler import WeiboCrawler


basepath = sys.argv[0]
if basepath.find("/") !=  -1:
	basepath = basepath[:basepath.find("/")]
else:
	basepath = "."


class ProfileFiller:
	def __init__(self, username, password, proxy=None):
		self.wc = WeiboCrawler()
		self.wc.login(username, password, proxy)
		self.is_login = False
		if self.wc.is_login:
			self.is_login = True

	def isLogin(self):
		return self.is_login

	def fillProfile(self, kwds):
		nick = kwds['nick']
		self.wc.setNick(nick)

		domain = kwds['domain']
		self.wc.setDomain(domain)

		description = kwds['description']
		self.wc.setDescription(description)

		tag = kwds['tag']
		self.wc.setTag(tag)

		gender = kwds['gender']
		self.wc.setGender(gender)

		provid, cityid = kwds['location']['provid'], kwds['location']['cityid']
		self.wc.setLocation(provid, cityid)

		schoolid, inyear, department = kwds['school']['id'], kwds['school']['in'], kwds['school']['department']
		self.wc.setSchool(schoolid, inyear, department)

		companyname, inyear, outyear, department = kwds['company']['name'], kwds['company']['in'], kwds['company']['out'], kwds['company']['department']
		self.wc.setCompany(companyname, inyear, outyear, department)

		year, month, day = kwds['birth']['year'], kwds['birth']['month'], kwds['birth']['day']

		#picpath, mime, picname = kwds['pic']['path'], kwds['pic']['mime'], kwds['pic']['name']
		#self.wc.setAvatar(picpath, mime, picname)

if __name__ == "__main__":
#	account_file = sys.argv[1].strip()
#	profile_file = sys.argv[2].strip()

	valid_account = open("%s/acctOld.txt" % basepath, "a")
	valid_profile = open("%s/profileOld.txt" % basepath, "a")
	account_queue = Queue.Queue()
	profile_queue = Queue.Queue()

	with open("%s/acctNew.txt" % basepath, "r") as accounts:
		for account in accounts:
			items = account.strip().split("|")
			username = items[0]
			password = items[1]
			account_queue.put((username, password))

	print "account queue length:", account_queue.qsize()

	with open("%s/profileNew.txt" % basepath, "r") as profiles:
		for profile in profiles:
			pitems = profile.strip().split("|")
			profile = {}
			profile['nick'] = pitems[1]
			profile['domain'] = pitems[2]
			profile['description'] = pitems[3]
			profile['tag'] = pitems[4]
			profile['gender'] = pitems[5]

			profile['location'] = {}
			profile['location']['provid'], profile['location']['cityid'] = pitems[6].split(",")
			
			profile['school'] = {}
			profile['school']['id'] = pitems[7]
			profile['school']['in'] = "2002"
			profile['school']['department'] = "计算机科学与技术"

			profile['company'] = {}
			profile['company']['name'] = pitems[8]
			profile['company']['in'] = "2009"
			profile['company']['out'] = ""
			profile['company']['department'] = ""

			profile['birth'] = {}
			profile['birth']['year'], profile['birth']['month'], profile['birth']['day'] = pitems[9].split(",")

			profile['pic'] = {}
			profile['pic']['path'] = "%s/%s" % (basepath, pitems[10])
			profile['pic']['mime'] = "image/jpeg"
			profile['pic']['name'] = pitems[10]
			profile_queue.put(profile)

	print "profile queue length:", profile_queue.qsize()

	while (not account_queue.empty()) and (not profile_queue.empty()):
		profile = profile_queue.get()
		print profile
		profile_queue.task_done()

		while True:
			if account_queue.empty():
				break
			username, password = account_queue.get()
			print username, password
			account_queue.task_done()
			pf = ProfileFiller(username, password)
			if pf.isLogin():
				pf.fillProfile(profile)
				break

#	for profiled in fileinput.input("%s/profileNew.txt" % basepath, inplace=1):
#		pitems = profiled.strip().split()
#		if pitems[0] == "1":
#			print profiled
#
#		profile = {}
#		profile['nick'] = pitems[1]
#		profile['domain'] = pitems[2]
#		profile['description'] = pitems[3]
#		profile['tag'] = pitems[4]
#		profile['gender'] = pitems[5]
#
#		profile['location'] = {}
#		profile['location']['provid'], profile['location']['cityid'] = pitems[6].split(",")
#		
#		profile['school'] = {}
#		profile['school']['id'] = pitems[7]
#		profile['school']['in'] = "2002"
#		profile['school']['out'] = "2006"
#		profile['school']['department'] = "计算机科学与技术"
#
#		profile['company'] = {}
#		profile['company']['name'] = pitems[8]
#		profile['company']['in'] = "2009"
#		profile['company']['out'] = ""
#		profile['company']['department'] = ""
#
#		profile['birth'] = {}
#		profile['birth']['year'], profile['birth']['month'], profile['birth']['day'] = pitems[9].split(",")
#
#		profile['pic'] = {}
#		profile['pic']['path'] = "%s/%s" % (basepath, pitems[10])
#		profile['pic']['mime'] = "image/jpeg"
#		profile['pic']['name'] = pitems[10]
#
#		while True:
#			username, password = account_queue.get()
#			account_queue.task_done()
#			pf = ProfileFiller(username, password)
#			if not pf.isLogin():
#				continue	
#			pf.fillProfile(profile)
#			valid_account.write("%s|%s\n" % (username, password))
#			break
#
#		print "1%s" % profiled[1:]

#	for line in accounts:
#		items = line.strip().split("|")
#		username = items[0]
#		password = items[1]
#
#		print "%s, %s" % (username, password)
#
#		pf = ProfileFiller(username, password)
#		if not pf.isLogin():
#			continue
#
#		valid_account.write("1|%s|%s\n" % (username, password))
#
#
#		for profiled in fileinput.input("profileNew.txt", inplace=1):
#			pitems = profiled.strip().split()
#			if pitems[0] == "1":
#				continue
#
#			profile = {}
#			profile['nick'] = pitems[1]
#			profile['domain'] = pitems[2]
#			profile['description'] = pitems[3]
#			profile['tag'] = pitems[4]
#			profile['gender'] = pitems[5]
#
#			profile['location'] = {}
#			profile['location']['provid'], profile['location']['cityid'] = pitems[6].split(",")
#			
#			profile['school'] = {}
#			profile['school']['id'] = pitems[7]
#			profile['school']['in'] = "2002"
#			profile['school']['out'] = "2006"
#			profile['school']['department'] = "计算机科学与技术"
#
#			profile['company'] = {}
#			profile['company']['name'] = pitems[8]
#			profile['company']['in'] = "2009"
#			profile['company']['out'] = ""
#			profile['company']['department'] = ""
#
#			profile['birth'] = {}
#			profile['birth']['year'], profile['birth']['month'], profile['birth']['day'] = pitems[9].split(",")
#
#			profile['pic'] = {}
#			profile['pic']['path'] = "%s/%s" % (basepath, pitems[10])
#			profile['pic']['mime'] = "image/jpeg"
#			profile['pic']['name'] = pitems[10]
#
#			pf.fillProfile(profile)
#
#			print "1%s" % profiled[1:]
#			break
#	valid_account.close()
#	accounts.close()

	

#	account_list = []
#	with open("account_file", "r") as accounts:
#		for account in accounts:
#			items = account.strip().split("|")
#			username = items[0]
#			password = items[1]
#			account_list.append((username, password))

#	profile_queue = Queue.Queue() 
#	with open("profile_file", "r") as profiles:
#		for profile in profiles:
#			items = profile.strip().split("|")
#
#	for account in account_list:
#		pf = ProfileFiller(account[0], account[1], account[2])
#		if not pf.isLogin():
#			continue
#
#		profile = profile_queue.get()
