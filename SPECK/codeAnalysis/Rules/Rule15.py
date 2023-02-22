#!/usr/bin/python3

from Rules import *
from XmlReader import *
from Parser import *
from R import *
import sys


'''
RULE N°15

+ Don't use dangerous custom permissions
-> https://developer.android.com/training/articles/security-tips#CreatingPermissions

? Pseudo Code:
	1. Look for custom permissions with the ‘dangerous’ protection level

! Output
	-> NOTHING	: no dangerous custom permission found
	-> CRITICAL	: dangerous custom permission found
'''

class Rule15(Rules):
	def __init__(self, directory, database, verbose=True, verboseDeveloper=False, storeManager=None, flowdroid=False, platform="",validation=False, quiet=True):
		Rules.__init__(self, directory, database, verbose, verboseDeveloper, storeManager, flowdroid, platform, validation, quiet)

		self.AndroidErrMsg = "custom permission(s) with the ‘dangerous’ protection level (were) found"
		self.AndroidOkMsg = "no custom permission with the ‘dangerous’ protection level was found"
		self.AndroidText = "https://developer.android.com/training/articles/security-tips#CreatingPermissions"

		self.errMsg = "Don't use custom permission with the ‘dangerous’ protection level"
		self.category = R.CAT_3
		
		self.findXml()
		self.show(15, "Don't use dangerous custom permissions")

	def getDangerousCustom(self, permissions):
		dangerous = []

		for p in permissions:
			for arg in p[XmlReader.ARGS]:
				if 'android:protectionLevel="dangerous"' in arg:
					dangerous.append(p)
					break

		return dangerous

	def run(self):
		self.loading()
		if self.manifest != None:
			xmlReader = XmlReader(self.manifest)

			permissions	= xmlReader.getArgsTag("permission")
			dangerous = self.getDangerousCustom(permissions)
			
			# format data to be display in 'Display' class
			NotIn = xmlReader.constructToken(dangerous)
			# Set log msg
			NotIn 	= Parser.setMsg(NotIn, R.CRITICAL, self.errMsg)

			self.updateCN(xmlReader.getFile(), NotIn)

			self.loading()
			xmlReader.close()

			self.store(15, self.AndroidOkMsg, self.AndroidErrMsg, self.AndroidText, self.category, True)
			self.display(XmlReader)

		else:
			self.loading()


