#!/usr/bin/env python

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


rePackageName = r'(?s)(?<=<td class="wrap"><a href="/pkgbase/).+?(?=/">)'
reUpdateTime = """(?s)(?<=<th>Last Updated: </th>
			<td>).+?(?=</td>)"""


##########################################
#			Helper Functions			 #
##########################################
def getPackageName(body):
	sss = rePackageName.format()
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

def getHttpResponseString():
	resp = urllib.request.urlopen(site)
	return resp.read().decode("utf-8")

def clonePackage(package):
	pkgPath = CLONE_PATH + package.name
	bkpPath = CLONE_PATH + package.name + ".bkp"

	if(os.path.isdir(bkpPath)):
		call(["rm", "-rf", bkpPath])

	if(os.path.isdir(pkgPath)):
		print("creating backup")
		call(["mv", pkgPath, bkpPath])

	call(["mkdir", pkgPath])
	call(["git", "clone", package.gitPath, pkgPath])

def makeThePkg(package):
	cwd = os.getcwd()
	pkgPath = CLONE_PATH + package.name
	os.chdir(pkgPath)
	call(["makepkg", "-sri"])
	os.chdir(cwd)

##########################################
#			  Status Flags				 #
##########################################
forceUpdate = False
debug = False
nothingToUpdate = True


##########################################
#			Argv Parasing				 #
##########################################
for v in sys.argv:
	if v == "-f" or v == "-force":
		forceUpdate = True
	if v == "-d" or v == "-debug":
		debug = True


##########################################
#				Main Loop				 #
##########################################
with open(CONFIG_FILE, "r") as f:
	for site in f:
		site.rstrip()
		pack = Package()
		respString = getHttpResponseString()

		pack.name = getPackageName(respString)
		pack.updateTime = parseDateString(getUpdateTime(respString))
		pack.gitPath = AUR_CLONE_URL + pack.name + ".git"
		pack.localPath = CLONE_PATH + pack.name + "/PKGBUILD"

		if os.path.isfile(pack.localPath):
			pack.installTime = os.path.getmtime(pack.localPath)
			timeDif = pack.updateTime - pack.installTime
		else:
			clonePackage(pack)
			exit()

		if debug == True:
			print("{}, {}".format(pack.name, pack.updateTime))
			print("{}".format(pack.updateTime))
			print("Git Path: {}".format(pack.gitPath))
			print("{} last modified local: {}".format(pack.name, pack.installTime))
			print("file time dif = {}".format(timeDif))
		#else:
		#	os.system('clear')


		if (timeDif > 0) or (forceUpdate == True):
			update = False
			nothingToUpdate = False
			while 1:
				print("Update {} (y/n)?".format(pack.name))
				userResp = input("")
				if (userResp == "y") or (userResp == "Y") or (userResp == "yes") or (userResp == "Yes"):
					update = True
					break
				elif (userResp == "n") or (userResp == "N") or (userResp == "no") or (userResp == "No"):
					break
				else:
					print("Invalid Response")
			if update == True:
				clonePackage(pack)
				makeThePkg(pack)
		else:
			print("{} is up to date".format(pack.name))

	if nothingToUpdate == True:
		print("Everything is up to date!")
