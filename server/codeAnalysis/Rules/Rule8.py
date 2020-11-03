#!/usr/bin/python3

from Rules import *
from FileReader import *
from Parser import *
from R import *
import sys


'''
RULE N°8

+ Store private data within internal storage
** Store all private user data within the device's internal storage, which is sandboxed per app.
-> https://developer.android.com/topic/security/best-practices#internal-storage

? Pseudo Code:
	1. Look for 'openFileOutput' function call
	2. Check if the argument given is 'Context.MODE_PRIVATE'

! Output
	-> NOTHING	: no 'openFileOutput' found
	-> OK 	   	: MODE_PRIVATE used
	-> WARNING	: MODE_PRIVATE not used
'''

class Rule8(Rules):
	def __init__(self, directory, database, verbose=True, verboseDeveloper=False, storeManager=None, flowdroid=False, platform="",validation=False, quiet=True):
		Rules.__init__(self, directory, database, verbose, verboseDeveloper, storeManager, flowdroid, platform, validation, quiet)

		self.AndroidErrMsg = "call(s) to internal storage (are) not private"
		self.AndroidOkMsg = "call(s) to internal storage (are) private"
		self.AndroidText = "https://developer.android.com/topic/security/best-practices#internal-storage"

		self.okMsg = "Data stored in internal storage are private"		
		self.errMsg = "Store in internal storage only non sensitive data"
		self.category = R.CAT_4
		
		self.filter('android.content.Context')
		self.show(8, "Store private data within internal storage")

	def checkArgument(self, found):
		In = []
		NotIn = []
		for f in found:
			if f[R.VALUE] == "MODE_PRIVATE" or f[R.VALUE] == '0':
				In.append(f)
			else:
				NotIn.append(f)
		return In, NotIn


	def run(self):
		self.loading()

		for f in self.javaFiles:
			fileReader = FileReader(f)

			found = Parser.finder(fileReader, 
								[[Parser.findArgName, ('openFileOutput', 1, None)]
								])[0]

			In, NotIn = self.checkArgument(found)

			# Set log msg
			In = Parser.setMsg(In, R.OK)
			NotIn = Parser.setMsg(NotIn, R.WARNING, self.errMsg)

			self.updateOWN(f, In, NotIn, (len(found) == 0))
			self.loading()
			fileReader.close()

		self.store(8, self.AndroidOkMsg, self.AndroidErrMsg, self.AndroidText, self.category)
		self.display(FileReader)
	

