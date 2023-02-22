#!/usr/bin/python3

from Rules import *
from FileReader import *
from Parser import *
from R import *
from Common import *
import sys
import pathlib


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

	
	def run(self):
		self.loading()

		violations = []

		xmlReader = XmlReader(self.manifest)

		if self.manifest != None:
			# XML LOGIC
			sdkArgs = Common.get_xml_tag_args(xmlReader, 'uses-sdk')
			isNewSdk = False
			args = sdkArgs[0]['args'] 				
			argIndex, argValue = Common.get_arg_index_and_value(args, 'android:minSdkVersion=')
			if argIndex >= 0: 
			    if int(argValue) > 18:		# Check if SDK is > 18: if yes, the rule is always respected
			        isNewSdk = True

			violations = Common.set_err_msg(violations, self.errMsg)

			try:
				self.just_update(violations[0]["filepath"], violations)
			except Exception as e:
				pass

			self.loading()

			# Java LOGIC
			for f in self.javaFiles:
				fileReader = FileReader(f)

				if isNewSdk: 					
					print(f"Rule is always respected: minSdkVersion = {argValue} ( > 18 )\n")
					break
				_, _, violations = Common.check_call_and_arg(fileReader, 'openFileOutput', 1, ['MODE_PRIVATE', '0'])

				# Set log msg
				violations = Parser.setMsg(violations, R.WARNING, self.errMsg)

				# self.just_update(f, violations)
				self.updateWN(f, violations)
				self.loading()
				fileReader.close()

			self.store(11, self.AndroidOkMsg, self.AndroidErrMsg, self.AndroidText, self.category, True)
			self.display(FileReader)
			xmlReader.close()


