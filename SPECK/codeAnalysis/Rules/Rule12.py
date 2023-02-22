#!/usr/bin/python3

from Rules import *
from FileReader import *
from Parser import *
from R import *
from Common import *
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

	def run(self):
		self.loading()
		output = []
		for f in self.javaFiles:

			fileReader = FileReader(f)
		
			_, _, violations = Common.check_call_and_arg(fileReader, 'getSharedPreferences', 1, ['MODE_PRIVATE', '0'])
			fileReader.resetCursor()
			_, _, v2 = Common.check_call_and_arg(fileReader, 'getPreferences', 0, ['MODE_PRIVATE', '0'])
			violations += v2
			cpy = violations.copy()
			for n in cpy:
				if 'SharedPreferencesHelper' in n[R.INSTR]:
					violations.remove(n)

			# Set log msg
			# violations = Common.set_err_msg(violations, self.errMsg)

			# if len(violations) > 0:		# Then, violation(s) found
			# 	for i,v in enumerate(violations):
			# 		########################################
			# 		#    FIRST: check value has quotes     #
			# 		########################################
			# 		v_args = Common.get_func_args(v['instr'].split('getSharedPreferences')[1])

			# 		# name is IMPORTANT -> is the value we search for or it gives hints to the value we search for
			# 		name = v_args[0]	

			# 		output += Common.chase_value(fileReader, self.directory, name, v)

			self.just_update(f, violations)
			self.loading()
			fileReader.close()

		# print(f'OUTPUT: {len(output)}\n')
		# output = Common.get_unique(output) # make it unique
		# for o in output:
		# 	print(o)
		# print()

		self.store(12, self.AndroidOkMsg, self.AndroidErrMsg, self.AndroidText, self.category)
		self.display(FileReader)
	

