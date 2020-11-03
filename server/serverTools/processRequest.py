#!/usr/bin/python3

import subprocess, os, sys
sys.path.insert(0, 'codeAnalysis/')
sys.path.insert(0, 'codeAnalysis/Rules/')
from apk_crawler import *
from Storage import *
from Rule1 import *
from Rule2 import *
from Rule3 import *
from Rule4 import *
from Rule5 import *
from Rule6 import *
from Rule7 import *
from Rule8 import *
from Rule9 import *
from Rule10 import *
from Rule11 import *
from Rule12 import *
from Rule13 import *
from Rule14 import *
from Rule15 import *
from Rule16 import *
from Rule17 import *
from Rule18 import *
from Rule19 import *
from Rule20 import *
from Rule21 import *
from Rule22 import *
from Rule23 import *
from Rule24 import *
from Rule25 import *
from Rule26 import *
from Rule27 import *
from Rule28 import *
from Rule29 import *
from Rule30 import *
from Rule31 import *
from Rule32 import *

'''
##? DATA STRUCTURE USED

* ERROR SERVER -> CLIENT: warn a client that an error has occurred
$ "error=..."

* INFO SERVER -> CLIENT: keep update the client about steps achieved
$ "status=..."

* DATA CLIENT -> SERVER: make a request to the server
$ "packageName=...&versionName=...&appName=..."

* DATA SERVER -> CLIENT: send data results to the client
$ "packageName=...&versionName=...&appName=...&stats=...+...+...&criticals=Issue_Title@Issue_Category@Issue_Description+...@...@...&warnings=...@...@...+...@...@...&infos=...@...@...+...@...@..."

% stats = nb critical issues, nb warning issues, nb guidelines respected
% criticals, warnings, info = kind of security issue (description)
'''

download_directory = "download"

JADX_CST_DIR = "/resources/AndroidManifest.xml"

class ProcessRequest():
	def __init__(self, ip, port):
		self.error_message = ""
		self.ip = ip
		self.port = port

	def get_error(self):
		return self.error_message

	def set_error(self, msg):
		self.error_message = msg

	def parse_request(self, client_request):
		packageName = ""
		versionName = ""
		appName = ""

		# client_request = "packageName:...,versionName:..."
		elems = client_request.split('&')
		for e in elems:
			fields = e.split('=')
			arg = fields[0]
			if (len(fields) > 1):
				val = fields[1]
			else:
				val = ""

			if (arg == "packageName"):
				packageName = val
			elif (arg == "versionName"):
				versionName = val
			elif (arg == "appName"):
				appName = val

		self.packageName = packageName
		self.versionName = versionName
		self.appName = appName


	def download_apk(self, server, timeout):
		if self.get_error() != "" or server.broken_pipe():
			return ""

		print("[*] (%s:%s) >> Looking for %s on apkpure.com" % (self.ip, self.port, self.packageName))
		dwl = Downloader(timeout, self.ip, self.port)
		dwl.APK_crawler(server, self.packageName, self.versionName)

		if (dwl.errorOccurred()):
			self.error_message = dwl.getError()
			print("\033[31m[*] (%s:%s) << %s\033[0m" % (self.ip, self.port, dwl.getError().split('=')[1]))

	def decompile_apk(self, server, timeout):
		if self.get_error() != "" or server.broken_pipe():
			return ""

		server.keep_client_update("Extracting source code", 3)
		print("[*] (%s:%s) >> Extracting %s" % (self.ip, self.port, self.packageName))

		try:
			subprocess.call("./apk2src/decompiler.sh "+ download_directory+"/"+self.packageName+".apk", shell=True, timeout=timeout)
		except:
			subprocess.call("ps -a | grep \"apk2src\" | awk '{print $1}' | xargs kill 2> /dev/null;", shell=True)

		dirOutput = download_directory + "/" + self.packageName

		# Check bash script success
		if (not os.path.isfile(dirOutput+JADX_CST_DIR)):
			self.error_message = "error=Source code can't be extracted"
			print("\033[31m[*] (%s:%s) << Extraction of '%s' failed\033[0m" % (self.ip, self.port, download_directory+"/"+self.packageName+".apk"))
		else:
			print("[*] (%s:%s) << %s.apk extracted" % (self.ip, self.port, self.packageName))

		return dirOutput

	def getManifestFile(self, manifest):
		data = "";
		with open(manifest) as f: 
			for line in f: 
				data += line
		return data

	def analyse_code(self, server, directoryName, flowdroid, platform):
		if self.get_error() != "" or server.broken_pipe():
			return ""

		# Option : send xml file
		server.send_manifest(self.getManifestFile(directoryName + JADX_CST_DIR).replace("\n", " "))
		###

		server.keep_client_update("Analysing source code", 4)
		print("[*] (%s:%s) >> Analysing of %s" % (self.ip, self.port, self.packageName))

		data = "packageName="+self.packageName+"&versionName="+self.versionName+"&appName="+self.appName
		
		# Code Analysing
		func = [Rule1, Rule2, Rule3, Rule4, Rule5, Rule6, Rule7,
				Rule8, Rule9, Rule10, Rule11, Rule12, Rule13, Rule14,
				Rule15, Rule16, Rule17, Rule18, Rule19, Rule20, Rule21,
				Rule22, Rule23, Rule24, Rule25, Rule26, Rule27, Rule28,
				Rule29, Rule30, Rule31, Rule32]
				
		storageManager = Storage()

		index = 1
		nbRules = len(func)
		for r in func:
			if self.get_error() != "" or server.broken_pipe():
				return ""
			print("\033[94m[$] (%s:%s) >> %d/%d\033[0m" % (self.ip, self.port, index, nbRules))
			# rulefct = r(directoryName, "_default", False, False, storageManager, flowdroid, platform)
			rulefct = r(directoryName, None, False, False, storageManager, flowdroid, platform)
			rulefct.run()
			index += 1

		nbcriticals, nbwarnings, nbinfos, criticals, warnings, infos = storageManager.get()

		'''
		nbcriticals = 2
		nbwarnings  = 5
		nbinfos     = 3
		criticals = ["Security issue 1#This is the security issue description", "Security issue 2#This is the security issue description"]
		warnings  = ["Security warning 1#This is the security warning description", "Security warning 2#This is the security warning description", "Security warning 3#This is the security warning description"]
		infos     = ["Security info 1#This is the security info description", "Security info 2#This is the security info description"]
		'''

		data += "&stats="     +str(nbcriticals)+"+"+str(nbwarnings)+"+"+str(nbinfos)
		data += "&criticals=" +"+".join(str(x) for x in criticals)
		data += "&warnings=" +"+".join(str(x) for x in warnings)
		data += "&infos=" +"+".join(str(x) for x in infos)

		print("[*] (%s:%s) << Source code of %s was analysed" % (self.ip, self.port, self.packageName))

		return data.encode()




