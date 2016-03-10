#!/usr/bin/env python
'''
1. List all repos in a text file

2. Iterate through all items in text file
	download makepkg, dif with current on drive
	if not different delete makepkg

'''

import sys
import urllib.request
import re
import datetime
import pytz
import os
import time
from package import Package
from subprocess import call

AUR_CLONE_URL = "https://aur.archlinux.org/"
CLONE_PATH = "/home/cdo/AUR/"
CONFIG_FILE = "list.txt"


rePackageName = r'(?s)(?<=/pkgbase/atom-editor/">).+?(?=</a></td>)'
reUpdateTime = """(?s)(?<=<th>Last Updated: </th>
			<td>).+?(?=</td>)"""

def getPackageName(body):
	r = re.search(rePackageName, body)
	return r.group()

def getUpdateTime(body):
	r = re.search(reUpdateTime, body)
	return r.group()

def getGitUrl(body):
	r = re.search(reGitPath, body)
	return r.group()

def parseDateString(dateString):
	dtObj = datetime.datetime.strptime(dateString, "%Y-%m-%d %H:%M")
	return dtObj.timestamp()

def clonePackage(package):
	pkgPath = CLONE_PATH + package.name
	if(os.path.isfile(pkgPath)):
		call(["mv", pkgPath, pkgPath + ".bkp"])
	call(["mkdir", pkgPath])
	call(["git", "clone", package.gitPath, pkgPath])

def getHttpResponseString():
	resp = urllib.request.urlopen(site)
	return resp.read().decode("utf-8")


########################################
#		Status Flags				   #
########################################
forceUpdate = False
debug = False


for v in sys.argv:
	if v == "-f" or v == "-force":
		forceUpdate = True
	if v == "-d" or v == "-debug":
		debug = True

with open(CONFIG_FILE, "r") as f:
	for site in f:
		site.rstrip()
		pack = Package()
		respString = getHttpResponseString()

		pack.name = packageName = getPackageName(respString)
		pack.updateTime = parseDateString(getUpdateTime(respString))
		pack.gitPath = AUR_CLONE_URL + pack.name + ".git"
		pack.localPath = CLONE_PATH + pack.name + "/PKGBUILD"
		#packageName = getPackageName(respString)
		#updateTime = parseDateString(getUpdateTime(respString))
		#gitPath = AUR_CLONE_URL + packageName + ".git"

		#packagePath = CLONE_PATH + packageName + "/PKGBUILD"

		if os.path.isfile(pack.localPath):
			pack.installTime = os.path.getmtime(pack.localPath)
			timeDif = pack.updateTime - pack.installTime
		else:
			clonePackage(packageName)
			exit()

		if debug == True:
			print("{}, {}".format(pack.name, pack.updateTime))
			print("{}".format(pack.updateTime))
			print("Git Path: {}".format(pack.gitPath))
			print("{} last modified local: {}".format(pack.name, pack.installTime))
			print("file time dif = {}".format(timeDif))


		if timeDif < 0:
			clonePackage(pack)
