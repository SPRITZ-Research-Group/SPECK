#!/usr/bin/python3

from Parser import *
from R import *

'''
Data Structure

apps = 
[
	{
		APPNAME=pkgName1,
		RESULTS=
				[
					{ 
						ID=ruleNb,
						TYPE=Severity,
						NB=NbIssues,
						…
					}, …
				]

	}, …
]

'''

class Storage():
	APPNAME  = "appName"
	RESULTS  = "res"

	ID 		 = "id"
	TYPE 	 = "type"
	NB 	 	 = "nb"
	MSG      = "msg"
	TOT		 = "tot"

	# All files
	CRITICAL = "c"
	WARNING  = "w"
	INFO 	 = "i"
	NOTHING  = "n"

	# Internal files
	INT_CRITICAL = "i_c"
	INT_WARNING  = "i_w"
	INT_INFO 	 = "i_i"

	# External files
	EXT_CRITICAL = "e_c"
	EXT_WARNING  = "e_w"
	EXT_INFO 	 = "e_i"


	def __init__(self):
		self.nbcriticals = 0
		self.nbwarnings  = 0
		self.nbinfos     = 0
		self.criticals	 = []
		self.warnings  	 = []
		self.infos     	 = []

		self.currentApp  = {}
		self.currentApp[Storage.RESULTS] = []
		self.apps		 = []


	def get(self):
		return self.nbcriticals, self.nbwarnings, self.nbinfos, self.criticals, self.warnings, self.infos


	def androidStats(self, AndroidOkMsg, AndroidErrMsg, AndroidText, results, nb, category, NothingButOk=False):
		localNbCriticals = 0
		localNbWarnings = 0
		localNbInfos = 0
		
		# COUNT
		for file in results:
			if R.CRITICAL in file[1]:
				self.nbcriticals += len(file[1][R.CRITICAL])
				localNbCriticals += len(file[1][R.CRITICAL])

			if R.WARNING in file[1]:
				self.nbwarnings += len(file[1][R.WARNING])
				localNbWarnings += len(file[1][R.WARNING])

			if R.OK in file[1]:
				self.nbinfos += len(file[1][R.OK])
				localNbInfos += len(file[1][R.OK])

		if NothingButOk:
			self.infos.append(AndroidOkMsg + "@" + category + "@" + AndroidText)

		# SET TEXT
		if localNbCriticals > 0:
			self.criticals.append(str(localNbCriticals) + " " + self.formatMsg(AndroidErrMsg, localNbCriticals) + "@" + category + "@" + AndroidText)

		if localNbWarnings > 0:
			self.warnings.append(str(localNbWarnings) + " " + self.formatMsg(AndroidErrMsg, localNbWarnings) + "@" + category + "@" + AndroidText)

		if localNbInfos > 0:
			self.infos.append(str(localNbInfos) + " " + self.formatMsg(AndroidOkMsg, localNbInfos) + "@" + category + "@" + AndroidText)


	def plural2singular(self, msg):
		msg = msg.replace("()", "s")
		msg = msg.replace("(were)", "was")
		msg = msg.replace("(don't)", "doesn't")
		msg = msg.replace("(have)", "has")
		msg = msg.replace("(s)", "")
		msg = msg.replace("(are)", "is")
		msg = msg.replace("(ies)", "y")
		return msg


	def setPlural(self, msg):
		msg = msg.replace("(", "").replace(")", "")
		return msg


	def formatMsg(self, msg, nb):
		if nb > 1:
			msg = self.setPlural(msg)
		else:
			msg = self.plural2singular(msg)
		return msg


	def getGlobalStats(self):
		return self.apps


	def displayGlobalStats(self):
		print("\n\033[46m** SUMMARY **\033[0m")
		for app in self.apps:
			print(f"[+] {app[Storage.APPNAME]}")
			for elem in app[Storage.RESULTS]:
				if Storage.TYPE in elem:
					if elem[Storage.TYPE] == Storage.CRITICAL:
						print(f"\033[31m({elem[Storage.ID]}) {elem[Storage.NB]} {elem[Storage.MSG]}\033[0m")
					elif elem[Storage.TYPE] == Storage.WARNING:
						print(f"\033[33m({elem[Storage.ID]}) {elem[Storage.NB]} {elem[Storage.MSG]}\033[0m")
					elif elem[Storage.TYPE] == Storage.INFO:
						print(f"\033[32m({elem[Storage.ID]}) {elem[Storage.NB]} {elem[Storage.MSG]}\033[0m")

					elif elem[Storage.TYPE] == Storage.INT_CRITICAL:
						print(f"\033[31m[INTERNAL] ({elem[Storage.ID]}) {elem[Storage.NB]}/{elem[Storage.TOT]}\033[0m")
					elif elem[Storage.TYPE] == Storage.INT_WARNING:
						print(f"\033[33m[INTERNAL] ({elem[Storage.ID]}) {elem[Storage.NB]}/{elem[Storage.TOT]}\033[0m")
					elif elem[Storage.TYPE] == Storage.INT_INFO:
						print(f"\033[32m[INTERNAL] ({elem[Storage.ID]}) {elem[Storage.NB]}/{elem[Storage.TOT]}\033[0m")

					elif elem[Storage.TYPE] == Storage.EXT_CRITICAL:
						print(f"\033[31m[EXTERNAL] ({elem[Storage.ID]}) {elem[Storage.NB]}/{elem[Storage.TOT]}\033[0m")
					elif elem[Storage.TYPE] == Storage.EXT_WARNING:
						print(f"\033[33m[EXTERNAL] ({elem[Storage.ID]}) {elem[Storage.NB]}/{elem[Storage.TOT]}\033[0m")
					elif elem[Storage.TYPE] == Storage.EXT_INFO:
						print(f"\033[32m[EXTERNAL] ({elem[Storage.ID]}) {elem[Storage.NB]}/{elem[Storage.TOT]}\033[0m")

					elif elem[Storage.TYPE] == Storage.NOTHING:
						print(f"\033[32m({elem[Storage.ID]}) {elem[Storage.MSG]}\033[0m")

			print("")

	def displaySyntheticStats(self, ruleNb):

		keys = ["#int_bp", "#ext_bp", "#int_w", "#ext_w", "#int_gp", "#ext_gp"]

		for app in self.apps:
			res = [0, 0, 0, 0, 0, 0]
			for elem in app[Storage.RESULTS]:
				if Storage.TYPE in elem:
					if elem[Storage.ID] == ruleNb:
						if elem[Storage.TYPE] == Storage.INT_CRITICAL:
							res[0] += elem[Storage.NB]
						elif elem[Storage.TYPE] == Storage.EXT_CRITICAL:
							res[1] += elem[Storage.NB]
						elif elem[Storage.TYPE] == Storage.INT_WARNING:
							res[2] += elem[Storage.NB]
						elif elem[Storage.TYPE] == Storage.EXT_WARNING:
							res[3] += elem[Storage.NB]
						elif elem[Storage.TYPE] == Storage.INT_INFO:
							res[4] += elem[Storage.NB]
						elif elem[Storage.TYPE] == Storage.EXT_INFO:
							res[5] += elem[Storage.NB]

			print(f"{app[Storage.APPNAME]} {keys[0]} {res[0]} {keys[1]} {res[1]} {keys[2]} {res[2]} {keys[3]} {res[3]} {keys[4]} {res[4]} {keys[5]} {res[5]}")


	def setApp(self, appName):
		self.currentApp = {}
		self.currentApp[Storage.APPNAME] = appName
		self.currentApp[Storage.RESULTS] = []


	def commit(self):
		self.apps.append(self.currentApp)


	def checkFileCtgy(self, pkgDir, file):
		if ((pkgDir != None) and (pkgDir in file)) or ("AndroidManifest.xml" in file):
			return True
		return False


	def generateElem(self, Id, Type, Nb, Msg, Tot=None):
		elem = {}
		elem[Storage.ID] = Id
		elem[Storage.TYPE] 	= Type
		elem[Storage.NB] 	= Nb
		elem[Storage.MSG] 	= Msg
		elem[Storage.TOT]	= Tot
		return elem


	def globalStats(self, ruleId, AndroidOkMsg, AndroidErrMsg, AndroidText, results, nb, pkgDir, NothingButOk=False):
		localNbCriticals = 0
		localNbWarnings = 0
		localNbInfos = 0

		localNbCriticals_INT = 0
		localNbWarnings_INT = 0
		localNbInfos_INT = 0

		localNbCriticals_EXT = 0
		localNbWarnings_EXT = 0
		localNbInfos_EXT = 0
		
		# COUNT
		for file in results:
			if R.CRITICAL in file[1]:
				localNbCriticals += len(file[1][R.CRITICAL])
				if self.checkFileCtgy(pkgDir, file[0]):
					localNbCriticals_INT += len(file[1][R.CRITICAL])
				else:
					localNbCriticals_EXT += len(file[1][R.CRITICAL])

			if R.WARNING in file[1]:
				localNbWarnings += len(file[1][R.WARNING])
				if self.checkFileCtgy(pkgDir, file[0]):
					localNbWarnings_INT += len(file[1][R.WARNING])
				else:
					localNbWarnings_EXT += len(file[1][R.WARNING])

			if R.OK in file[1]:
				localNbInfos += len(file[1][R.OK])
				if self.checkFileCtgy(pkgDir, file[0]):
					localNbInfos_INT += len(file[1][R.OK])
				else:
					localNbInfos_EXT += len(file[1][R.OK])

		if NothingButOk:
			elem = {}
			elem[Storage.ID] = ruleId
			elem[Storage.TYPE] = Storage.NOTHING
			elem[Storage.MSG] 	= AndroidOkMsg
			self.currentApp[Storage.RESULTS].append(elem)

		if localNbCriticals > 0:
			self.currentApp[Storage.RESULTS].append(self.generateElem(ruleId, Storage.CRITICAL, localNbCriticals, self.formatMsg(AndroidErrMsg, localNbCriticals)))
		if localNbWarnings > 0:
			self.currentApp[Storage.RESULTS].append(self.generateElem(ruleId, Storage.WARNING, localNbWarnings, self.formatMsg(AndroidErrMsg, localNbWarnings)))
		if localNbInfos > 0:
			self.currentApp[Storage.RESULTS].append(self.generateElem(ruleId, Storage.INFO, localNbInfos, self.formatMsg(AndroidOkMsg, localNbInfos)))

		if localNbCriticals_INT > 0:
			self.currentApp[Storage.RESULTS].append(self.generateElem(ruleId, Storage.INT_CRITICAL, localNbCriticals_INT, self.formatMsg(AndroidErrMsg, localNbCriticals_INT), localNbCriticals))
		if localNbWarnings_INT > 0:
			self.currentApp[Storage.RESULTS].append(self.generateElem(ruleId, Storage.INT_WARNING, localNbWarnings_INT, self.formatMsg(AndroidErrMsg, localNbWarnings_INT), localNbWarnings))
		if localNbInfos_INT > 0:
			self.currentApp[Storage.RESULTS].append(self.generateElem(ruleId, Storage.INT_INFO, localNbInfos_INT, self.formatMsg(AndroidOkMsg, localNbInfos_INT), localNbInfos))

		if localNbCriticals_EXT > 0:
			self.currentApp[Storage.RESULTS].append(self.generateElem(ruleId, Storage.EXT_CRITICAL, localNbCriticals_EXT, self.formatMsg(AndroidErrMsg, localNbCriticals_EXT), localNbCriticals))
		if localNbWarnings_EXT > 0:
			self.currentApp[Storage.RESULTS].append(self.generateElem(ruleId, Storage.EXT_WARNING, localNbWarnings_EXT, self.formatMsg(AndroidErrMsg, localNbWarnings_EXT), localNbWarnings))
		if localNbInfos_EXT > 0:
			self.currentApp[Storage.RESULTS].append(self.generateElem(ruleId, Storage.EXT_INFO, localNbInfos_EXT, self.formatMsg(AndroidOkMsg, localNbInfos_EXT), localNbInfos))


	def save(self, ruleId, AndroidOkMsg, AndroidErrMsg, AndroidText, results, nb, category, pkgDir, NothingButOk=False):
		self.androidStats(AndroidOkMsg, AndroidErrMsg, AndroidText, results, nb, category, NothingButOk)
		self.globalStats(ruleId, AndroidOkMsg, AndroidErrMsg, AndroidText, results, nb, pkgDir, NothingButOk)


