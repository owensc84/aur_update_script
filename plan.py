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

def clonePackage(name):
	pkgPath = CLONE_PATH + name
	if(os.path.isfile(pkgPath)):
		call(["mv", pkgPath, pkgPath + ".bkp"])
	call(["mkdir", pkgPath])
	call(["git", "clone", gitPath, pkgPath])

def getHttpResponseString():
	resp = urllib.request.urlopen(site)
	return resp.read().decode("utf-8")



forceUpdate = False

for v in sys.argv:
	if v == "-f" or v == "-force":
		forceUpdate = True

with open(CONFIG_FILE, "r") as f:
	site = f.readline().rstrip()

respString = getHttpResponseString()

packageName = getPackageName(respString)
updateTime = parseDateString(getUpdateTime(respString))
gitPath = AUR_CLONE_URL + packageName + ".git"

packagePath = CLONE_PATH + packageName + "/PKGBUILD"

if os.path.isfile(packagePath):
	installTime = os.path.getmtime(packagePath)
	timeDif = updateTime - installTime
else:
	clonePackage(packageName)
	exit()


print("{}, {}".format(packageName, updateTime))
print("{}".format(updateTime))
print("Git Path: {}".format(gitPath))
print("{} last modified local: {}".format(packageName, installTime))
print("file time dif = {}".format(timeDif))


if timeDif < 0:
	clonePackage(packageName)
