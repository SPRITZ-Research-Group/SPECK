#!/usr/bin/python3

from Rules import *
from FileReader import *
from Parser import *
from R import *
import sys


'''
RULE N°11

+ Store only non-sensitive data in cache files
-> https://developer.android.com/topic/security/best-practices#cache

? Pseudo Code:
	1. Look for 'getExternalCacheDir()' and 'getCacheDir()'

! Output
	-> NOTHING	: no function found
	-> WARNING  : function found
'''

class Rule11(Rules):
	def __init__(self, directory, database, verbose=True, verboseDeveloper=False, storeManager=None, flowdroid=False, platform="",validation=False, quiet=True):
		Rules.__init__(self, directory, database, verbose, verboseDeveloper, storeManager, flowdroid, platform, validation, quiet)

		self.AndroidErrMsg = "function call(s) might store sensitive data in cache files"
		self.AndroidOkMsg = "no data is store in cache"
		self.AndroidText = "https://developer.android.com/topic/security/best-practices#cache"

		self.okMsg = "Cache files are not used"
		self.errMsg = "Don't store sensitive data in cache files"
		self.category = R.CAT_4
		
		self.filter('android.content.Context')
		self.show(11, "Store only non-sensitive data in cache files")


	def run(self):
		self.loading()

		for f in self.javaFiles:
			fileReader = FileReader(f)

			found = Parser.finder(fileReader, 
								[[Parser.findLine, ([['.getCacheDir()'], ['.getExternalCacheDir()']], None)]])[0]

			# Set log msg
			found = Parser.setMsg(found, R.WARNING, self.errMsg)

			self.updateWN(f, found)
			self.loading()
			fileReader.close()

		self.store(11, self.AndroidOkMsg, self.AndroidErrMsg, self.AndroidText, self.category, True)
		self.display(FileReader)


