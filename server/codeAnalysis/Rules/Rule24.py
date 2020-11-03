#!/usr/bin/python3

from Rules import *
from FileReader import *
from Parser import *
from R import *
import sys


'''
RULE N°24

+ Dynamically load code
** It's discourage to load code from outside of your application APK
-> https://developer.android.com/training/articles/security-tips#DynamicCode

? Pseudo Code:
	1. If DexClassLoader is used, discourage its use

! Output
	-> NOTHING	: no DexClassLoader found
	-> CRITICAL	: DexClassLoader found
'''

class Rule24(Rules):
	def __init__(self, directory, database, verbose=True, verboseDeveloper=False, storeManager=None, flowdroid=False, platform="",validation=False, quiet=True):
		Rules.__init__(self, directory, database, verbose, verboseDeveloper, storeManager, flowdroid, platform, validation, quiet)

		self.AndroidErrMsg = "time(s) dynamic code loading (were) found"
		self.AndroidOkMsg = "no dynamic code loading was found"
		self.AndroidText = "https://developer.android.com/training/articles/security-tips#DynamicCode"

		self.okMsg = "No dynamic code loading is used"
		self.errMsg = "Its discourage to load code from outside of your application APK"
		self.category = R.CAT_NA
		
		self.filter('dalvik.system.DexClassLoader')
		self.show(24, "Dynamically load code")

	def run(self):
		self.loading()

		for f in self.javaFiles:
			fileReader = FileReader(f)

			# Look for depreciated functions
			found = Parser.finder(fileReader, 
								[[Parser.findLine, ([['DexClassLoader', 'new']], None)]])[0]

			# Set log msg
			found = Parser.setMsg(found, R.CRITICAL, self.errMsg)

			self.updateCN(f, found)
			self.loading()
			fileReader.close()

		self.store(24, self.AndroidOkMsg, self.AndroidErrMsg, self.AndroidText, self.category, True)
		self.display(FileReader)

