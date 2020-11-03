#!/usr/bin/python3

from FileReader import *
from Parser import *
from R import *
import os
import json
import pymongo

class StoreJson():
	outputcol = None

	@staticmethod
	def initMongoDb(database_name):
		if database_name == None:
			return

		if StoreJson.outputcol:
			return

		myclient = pymongo.MongoClient("mongodb://localhost:27017/")
		mydb = myclient[database_name]

		StoreJson.outputcol = mydb["data"]
		StoreJson.rulestats = mydb["rulestats"]

	@staticmethod
	def store(collection, rec, database_name):
		if not rec:
			return

		if database_name == None:	# database is not in use
			return

		if not StoreJson.outputcol:
			StoreJson.initMongoDb(database_name)

		if collection == "outputcol":
			StoreJson.outputcol.insert_one(rec)
		elif collection == "rulestats":
			StoreJson.rulestats.insert_one(rec)
		else:
			print("Collection {} does not exist!!".format(collection))
			exit(0)

	@staticmethod
	def showResults(results, nb, Reader, packageDir, validation, nr, apk, database=None, errorMsg=""):

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

						StoreJson.store("outputcol", myRecord, database)
