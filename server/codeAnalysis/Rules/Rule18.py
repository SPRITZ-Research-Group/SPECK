#!/usr/bin/python3

from Rules import *
from FileReader import *
from Parser import *
from R import *
import sys


'''
RULE N°18

+ Prefer explicit intents
-> https://developer.android.com/training/articles/security-tips#use-intents

? Pseudo Code:
	1. Get intents used in 'bindService', 'startService' or 'sendOrderedBroadcast'
	2. Check if these intents are explicits

! Output
	-> NOTHING	: no implicit intent found in 'bindService', 'startService' or 'sendOrderedBroadcast'
	-> CRITICAL	: implicit intent found in 'bindService', 'startService' or 'sendOrderedBroadcast'
'''

class Rule18(Rules):
	def __init__(self, directory, database, verbose=True, verboseDeveloper=False, storeManager=None, flowdroid=False, platform="",validation=False, quiet=True):
		Rules.__init__(self, directory, database, verbose, verboseDeveloper, storeManager, flowdroid, platform, validation, quiet)

		self.AndroidErrMsg = "implicit intent(s) might execute an android component untrusted"
		self.AndroidOkMsg = "no implicit intent(s) might execute an android component untrusted"
		self.AndroidText = "https://developer.android.com/training/articles/security-tips#use-intents"

		self.errMsg = "Implicit intent might execute an android component untrusted"
		self.category = R.CAT_1
		
		self.filter('android.content.Intent')
		self.show(18, "Prefer explicit intents")

	def checkIfExplicit(self, In):
		NotIn = []

		for e in In:
			if ".class" not in e[R.INSTR]:
				NotIn.append(e)

		return NotIn

	def checkArg(self, fctCallingIntent):
		NotIn = []

		fctList = ['bindService', 'startService', 'sendOrderedBroadcast']

		for e in fctCallingIntent:
			for fct in fctList:
				if fct in e[R.INSTR]:
					if ("new" and "Intent") in e[R.INSTR]:
						if not (".class" in e[R.INSTR]):
							NotIn.append(e)
					break

		return NotIn

	def run(self):
		self.loading()
		for f in self.javaFiles:
			fileReader = FileReader(f)

			found = Parser.finder(fileReader,
									[[Parser.findVarName, (['Intent '], None)],
									 [Parser.findVarName, (['Intent', 'new'], None)],
									 [Parser.findArgName, ('bindService', 0, None)],
									 [Parser.findArgName, ('startService', 0, None)],
									 [Parser.findArgName, ('sendOrderedBroadcast', 0, None)]])

			intents = found[0]
			intentsInstatiation = found[1]
			fctCallingIntent = found[2] + found[3] + found[4]

			intents = Parser.setScopes(intents)
			intentsInstatiation = Parser.setScopesWith(intentsInstatiation, intents)

			# 'In' will contain all intents used by 'bindService', 'startService’, 'sendOrderedBroadcast' or 'startActivity'
			In, NotIn = Parser.diff(intentsInstatiation, fctCallingIntent)
			
			# Check if intents are explicit or implicit
			NotIn = self.checkIfExplicit(In)
			# Case where intent is instantiated in an argument position
			NotIn2 = self.checkArg(fctCallingIntent)

			NotIn = NotIn + NotIn2

			# Set log msg
			NotIn 	= Parser.setMsg(NotIn, R.CRITICAL, self.errMsg)

			self.updateCN(f, NotIn)
			self.loading()
			fileReader.close()

		self.store(18, self.AndroidOkMsg, self.AndroidErrMsg, self.AndroidText, self.category, False, [self.errMsg])
		self.display(FileReader)

















