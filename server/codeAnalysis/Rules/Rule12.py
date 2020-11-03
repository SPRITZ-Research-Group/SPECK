#!/usr/bin/python3

from Rules import *
from FileReader import *
from Parser import *
from R import *
import sys


'''
RULE N°12

+ Use SharedPreferences in private mode
** When using getSharedPreferences() to create or access your app's SharedPreferences objects, use MODE_PRIVATE
-> https://developer.android.com/topic/security/best-practices#sharedpreferences

? Pseudo Code:
	1. Look for ‘getSharedPreferences()’
	2. Check if ‘MODE_PRIVATE’ argument is set

! Output
	-> NOTHING	: no 'getSharedPreferences' found
	-> OK 	   	: MODE_PRIVATE used
	-> CRITICAL	: MODE_PRIVATE not used
'''

class Rule12(Rules):
	def __init__(self, directory, database, verbose=True, verboseDeveloper=False, storeManager=None, flowdroid=False, platform="",validation=False, quiet=True):
		Rules.__init__(self, directory, database, verbose, verboseDeveloper, storeManager, flowdroid, platform, validation, quiet)

		self.AndroidErrMsg = "shared preference(s) saving (are) not private"
		self.AndroidOkMsg = "shared preference(s) saving (are) private"
		self.AndroidText = "https://developer.android.com/topic/security/best-practices#sharedpreferences"

		self.okMsg = "SharedPreferences is used in private mode"		
		self.errMsg = "Don't use SharedPreferences objects to share data"
		self.category = R.CAT_4
		
		self.filter('android.content.Context')
		self.show(12, "Use SharedPreferences in private mode")

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
								[[Parser.findArgName, ('getSharedPreferences', 1, None)]
								])[0]

			cpy = found.copy()
			for e in cpy:
				if 'SharedPreferencesHelper' in e[R.INSTR]:
					found.remove(e)
			
			In, NotIn = self.checkArgument(found)

			# Set log msg
			In = Parser.setMsg(In, R.OK)
			NotIn = Parser.setMsg(NotIn, R.CRITICAL, self.errMsg)

			self.updateOCN(f, In, NotIn, (len(found) == 0))
			self.loading()
			fileReader.close()

		self.store(12, self.AndroidOkMsg, self.AndroidErrMsg, self.AndroidText, self.category)
		self.display(FileReader)
	

