#!/usr/bin/python3

from FileReader import *
from Parser import *
from R import *
import os
import json
import pymongo

class MongoConfig():
	def __init__(self, db=None, host="localhost:27017", user=None, password=None):
		self.db = db
		self.host = host
		self.user = user
		self.password = password

class StoreJson():
	outputcol = None

	@staticmethod
	def initMongoDb(cfg: MongoConfig):
		if cfg.db == None:
			return

		if StoreJson.outputcol:
			return

		myclient = pymongo.MongoClient(f"mongodb+srv://{cfg.host}/", username=cfg.user, password=cfg.password)
		mydb = myclient[cfg.db]

		StoreJson.outputcol = mydb["data"]
		StoreJson.rulestats = mydb["rulestats"]

	@staticmethod
	def store(collection, rec, cfg: MongoConfig):
		if not rec:
			return

		if cfg.db == None:	# database is not in use
			return

		if StoreJson.outputcol == None:
			StoreJson.initMongoDb(cfg)

		if collection == "outputcol":
			outputcol_cursor = StoreJson.outputcol.find()		# retrieve all outputcol
			found = False
			# for x in outputcol_cursor:
			# 	if rec["apk"] == x["apk"] and rec["rule"] == x["rule"]:			# check if the analysis of the app was already done on the rule 
			# 		print(f"\033[1m\033[33m[!] App {rec['apk']} was already analysed on Rule {rec['rule']}!\033[0m\033[0m")
			# 		print(x)									# print the analysis previously stored
			# 		found = True
			# 		break
			if not found:										# if new analysis, then add its outputcol in the db
				StoreJson.outputcol.insert_one(rec)

		elif collection == "rulestats":
			rulestats_cursor = StoreJson.rulestats.find()		# retrieve all rulestats
			found = False
			for x in rulestats_cursor:
				if rec["apk"] == x["apk"] and rec["rule"] == x["rule"]:			# check if the analysis of the app was already done on the rule 
					print(f"\033[1m\033[35m[!] App {rec['apk']} was already analysed on Rule {rec['rule']}!\033[0m\033[0m")
					print(x)									# print the analysis previously stored
					found = True
					break
			if not found:										# if new analysis, then add its rulestats in the db
				StoreJson.rulestats.insert_one(rec)

		else:
			print(f"Collection {collection} does not exist!!")
			exit(0)


	@staticmethod
	def showResults(results, nb, Reader, packageDir, validation, nr, apk, mongo_cfg=None, errorMsg=""):
		for file in results:
			kind = "[EXTERNAL]"
			if ((packageDir != None) and (packageDir in file[0])) or ("AndroidManifest.xml" in file[0]):
				kind = "[INTERNAL]"

			for X in [R.WARNING, R.CRITICAL, R.OK]:
				if X in file[1] and len(file[1][X]) > 0:
					fileReader = Reader(file[0], False)
					lineNumber = -1
					for i in file[1][X]:
						if i[R.INSTR] != '':
							lineNumber = fileReader.getLine(i[R.INSTR], i)
							
							if lineNumber == -1:
								lineNumber = fileReader.getLine(i[R.INSTR][:30], i)

						else:
							lineNumber = -1
						
						myRecord = {}
						myRecord['severity'] = X
						myRecord['apk'] = apk
						myRecord['kind'] = kind
						myRecord['file'] = file[0]
						myRecord['lineNumber'] = lineNumber
						myRecord['rule'] = nr
						myRecord['errorMsg'] = errorMsg

						eMsg = ""
						for e in file[1][X]:
							if "eMsg" in e:
								eMsg = e["eMsg"]

						myRecord['eMsg'] = eMsg

						StoreJson.store("outputcol", myRecord, mongo_cfg)


