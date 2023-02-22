#!/usr/bin/python3

from Rules import *
from FileReader import *
from Parser import *
from R import *
from Common import *
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
		# self.show(18, "Prefer explicit intents")
		self.show(18, "Prefer explicit intents")


	def run(self):
		self.loading()
		fctList = ['bindService', 'startService', 'sendOrderedBroadcast']
		for f in self.javaFiles:
			fileReader = FileReader(f)

			intents = Common.get_all_var_names(fileReader, ['Intent '])
			intentsInstantiation = Common.get_all_var_names(fileReader, ['Intent', 'new'])
			fctCallingIntent = Common.get_all_arg_names(fileReader, 'bindService', 0)
			fctCallingIntent += Common.get_all_arg_names(fileReader, 'startService', 0)
			fctCallingIntent += Common.get_all_arg_names(fileReader, 'startActivity', 0)
			fctCallingIntent += Common.get_all_arg_names(fileReader, 'sendOrderedBroadcast', 0)

			# 'In' will contain all intents used by 'bindService', 'startService’, 'sendOrderedBroadcast' or 'startActivity'
			In, _ = Common.compare(intentsInstantiation, fctCallingIntent, with1=True, scope_with1=intents)
			
			# Check if intents are explicit or implicit
			NotIn = []
			for e in In:
				if ".class" not in e['instr']:
					NotIn.append(e)

			# Case where intent is instantiated in an argument position
			NotIn2 = []
			for e in fctCallingIntent:
				for fct in fctList:
					if fct in e['instr']:
						if ("new" and "Intent") in e['instr']:
							if not (".class" in e['instr']):
								NotIn2.append(e)
						break

			NotIn = NotIn + NotIn2

			# Set log msg
			NotIn 	= Parser.setMsg(NotIn, R.CRITICAL, self.errMsg)

			# not sure why this was added
			"""if len(NotIn) > 0:
				test = Common.get_all_var_types(fileReader, 'activity,')
				
				uriSetters = Common.get_all_obj_names(fileReader, 'setData')
				uriSetters += Common.get_all_obj_names(fileReader, 'setDataAndNormalize')
				uriSetters += Common.get_all_obj_names(fileReader, 'setDataAndType')
				uriSetters += Common.get_all_obj_names(fileReader, 'setDataAndTypeAndNormalize')


				# if len(uriSetters) > 0:
				# 	print(f'MAtch: {Common.match_obj_with_vars(NotIn, uriSetters)}')
				NotIn += uriSetters"""

			self.just_update(f, NotIn)
			self.loading()
			fileReader.close()

		self.store(18, self.AndroidOkMsg, self.AndroidErrMsg, self.AndroidText, self.category, False, [self.errMsg])
		self.display(FileReader)

