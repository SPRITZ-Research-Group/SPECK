#!/usr/bin/python3

from Rules import *
from FileReader import *
from Parser import *
from R import *
from Common import *
import sys


'''
RULE N°19

+ Use Android IPC
** Some applications use localhost network ports for handling sensitive IPC. You should not use this approach because these interfaces are accessible by other applications on the device.
-> https://developer.android.com/training/articles/security-tips#IPNetworking

? Pseudo Code:
	1. Look for ‘INADDR_ANY’, ‘localhost’ and ‘127.0.0.1’

! Output
	-> NOTHING	: no network ports are used to handle sensitive IPC
	-> WARNING	: network ports are used to handle sensitive IPC
'''

class Rule19(Rules):
	def __init__(self, directory, database, verbose=True, verboseDeveloper=False, storeManager=None, flowdroid=False, platform="",validation=False, quiet=True):
		Rules.__init__(self, directory, database, verbose, verboseDeveloper, storeManager, flowdroid, platform, validation, quiet)

		self.AndroidErrMsg = "network port(s) (are) used to handle sensitive IPC"
		self.AndroidOkMsg = "no network port is used to handle sensitive IPC"
		self.AndroidText = "https://developer.android.com/training/articles/security-tips#IPNetworking"

		self.errMsg = "Do not use localhost network ports for handling sensitive IPC"
		self.category = R.CAT_2
		
		self.filter(['java.net.Socket', 'java.net.ServerSocket'])
		self.show(19, "Use Android IPC")
	
	def run(self):
		self.loading()

		for f in self.javaFiles:
			fileReader = FileReader(f)

			# Look for depreciated functions
			found = Common.search_keywords(fileReader, ['INADDR_ANY', 'localhost', '127.0.0.1'], withStrings=True)

			# Set log msg
			found = Parser.setMsg(found, R.WARNING, self.errMsg)

			self.updateWN(f, found)
			self.loading()
			fileReader.close()

		self.store(19, self.AndroidOkMsg, self.AndroidErrMsg, self.AndroidText, self.category, True)
		self.display(FileReader)
