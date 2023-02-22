#!/usr/bin/python3

from Rules import *
from FileReader import *
from Parser import *
from R import *
import sys


'''
RULE N°31

+ Migrate existing data
** You should not migrate private user information, such as passwords or authorization tokens, to device encrypted storage.
-> https://developer.android.com/training/articles/direct-boot#migrating

? Pseudo Code:
	1. Look for ‘Context.moveSharedPreferencesFrom()’ or ‘Context.moveDatabaseFrom()’ functions 

! Output
	-> NOTHING	: 'moveSharedPreferencesFrom' or 'moveDatabaseFrom' not found
	-> WARNING	: 'moveSharedPreferencesFrom' or 'moveDatabaseFrom' found
'''

class Rule31(Rules):
	def __init__(self, directory, database, verbose=True, verboseDeveloper=False, storeManager=None, flowdroid=False, platform="",validation=False, quiet=True):
		Rules.__init__(self, directory, database, verbose, verboseDeveloper, storeManager, flowdroid, platform, validation, quiet)

		self.AndroidErrMsg = "time(s) private data might be compromised"
		self.AndroidOkMsg = "no private data is compromised"
		self.AndroidText = "https://developer.android.com/training/articles/direct-boot#migrating"

		self.errMsg = "You should not migrate private user information, such as passwords or authorization tokens, to device encrypted storage"
		self.category = R.CAT_4
		
		self.filter('android.content.Context')
		self.show(31, "Migrate existing data")

	def run(self):
		self.loading()

		for f in self.javaFiles:
			fileReader = FileReader(f)

			found = Parser.finder(fileReader, 
								[[Parser.findLine, ([['.moveSharedPreferencesFrom'], ['.moveDatabaseFrom']], None)]])[0]

			# Set log msg
			found = Parser.setMsg(found, R.WARNING, self.errMsg)

			self.updateWN(f, found)
			self.loading()
			fileReader.close()

		self.store(31, self.AndroidOkMsg, self.AndroidErrMsg, self.AndroidText, self.category, True)
		self.display(FileReader)







		

