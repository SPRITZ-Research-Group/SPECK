#!/usr/bin/python3

from Rules import *
from FileReader import *
from Parser import *
from R import *
import sys


'''
RULE N°13

+ Keep services and dependencies up-to-date
** Make sure that all libraries, SDKs, Google Play services, and other dependencies are up to date
-> https://developer.android.com/topic/security/best-practices#services-dependencies-updated
-> https://developer.android.com/training/articles/security-gms-provider

? Pseudo Code:
	1. Check if the app use Google Play services
	2. Check the Google Play services security provider

! Output
	-> NOTHING	: no google play services found
	-> OK 	   	: google play services are kept up-to-date
	-> CRITICAL	: google play services are not kept up-to-date
'''

class Rule13(Rules):
	def __init__(self, directory, database, verbose=True, verboseDeveloper=False, storeManager=None, flowdroid=False, platform="",validation=False, quiet=True):
		Rules.__init__(self, directory, database, verbose, verboseDeveloper, storeManager, flowdroid, platform, validation, quiet)

		self.AndroidErrMsg = "Google Play Services is not keep up-to-date"
		self.AndroidOkMsg = "Google Play Services is keep up-to-date"
		self.AndroidText = "https://developer.android.com/topic/security/best-practices#services-dependencies-updated"

		self.okMsg = "Google Play services is up-to-date"
		self.errMsg = "There is no check to know if Google Play services is up-to-date"
		self.category = R.CAT_NA
		
		self.filter('', True)
		self.show(13, "Keep services and dependencies up-to-date")

	def run(self):
		self.loading()
		
		# Check if Google Play Services is used
		if os.path.isdir(self.directory + '/sources/com/google/android/gms'):

			for f in self.javaFiles:
				fileReader = FileReader(f)

				search = Parser.finder(fileReader,
									[[Parser.findArgName, ('ProviderInstaller.installIfNeededAsync', 0, None)],
									 [Parser.findArgName, ('ProviderInstaller.installIfNeeded', 0, None)]])
				search = search[0] + search[1]
				
				if len(search) > 0:
					# Case where it's OK
					search = Parser.setMsg(search, R.OK)
					self.updateON(f, search)

				if len(search) > 0:
					self.loading(True)
					break
				else:
					self.loading()

				fileReader.close()

			# Case where there is no call to installIfNeededAsync or installIfNeeded
			if len(self.results) == 0:
				elem = {}
				elem[R.INSTR] = ''
				search = [elem]
				search = Parser.setMsg(search, R.CRITICAL, self.errMsg)
				
				self.updateC('nothing', search)
				
		else:
			self.updateN()

		self.store(13, self.AndroidOkMsg, self.AndroidErrMsg, self.AndroidText, self.category)
		self.display(FileReader)





		








