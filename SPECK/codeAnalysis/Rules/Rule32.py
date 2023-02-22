#!/usr/bin/python3

from Rules import *
from FileReader import *
from Parser import *
from R import *
import sys


'''
RULE N°32

+ Access device encrypted storage
** Use device encrypted storage only for information that must be accessible during Direct Boot mode. Don't use device encrypted storage as a general-purpose encrypted store. 
-> https://developer.android.com/training/articles/direct-boot#access

? Pseudo Code:
	1. Look for ‘.createDeviceProtectedStorageContext()’ function

! Output
	-> NOTHING	: 'createDeviceProtectedStorageContext' not found
	-> WARNING 	: 'createDeviceProtectedStorageContext' found
'''

class Rule32(Rules):
	def __init__(self, directory, database, verbose=True, verboseDeveloper=False, storeManager=None, flowdroid=False, platform="",validation=False, quiet=True):
		Rules.__init__(self, directory, database, verbose, verboseDeveloper, storeManager, flowdroid, platform, validation, quiet)

		self.AndroidErrMsg = "time(s) encrypted storage might be used as a general-purpose encrypted store"
		self.AndroidOkMsg = "no encrypted storage found"
		self.AndroidText = "https://developer.android.com/training/articles/direct-boot#access"

		self.errMsg = "Don't use device encrypted storage as a general-purpose encrypted store"
		self.category = R.CAT_5
		
		self.filter('android.content.Context')
		self.show(32, "Access device encrypted storage")

	def run(self):
		self.loading()

		for f in self.javaFiles:
			fileReader = FileReader(f)

			found = Parser.finder(fileReader, 
								[[Parser.findLine, ([['createDeviceProtectedStorageContext']], None)]])[0]

			# Set log msg
			found = Parser.setMsg(found, R.WARNING, self.errMsg)

			self.updateWN(f, found)
			self.loading()
			fileReader.close()

		self.store(32, self.AndroidOkMsg, self.AndroidErrMsg, self.AndroidText, self.category, True)
		self.display(FileReader)







		

