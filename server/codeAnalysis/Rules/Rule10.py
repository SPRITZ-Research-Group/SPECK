#!/usr/bin/python3

from Rules import *
from XmlReader import *
from Parser import *
from R import *
import sys


'''
RULE N°10

+ Use scoped directory access
** Limit app's access to a device's external storage
-> https://developer.android.com/topic/security/best-practices#external-storage
-> https://developer.android.com/training/articles/scoped-directory-access

? Pseudo Code:
	1. Check if READ_EXTERNAL_STORAGE or WRITE_EXTERNAL_STORAGE is set in manifest file

! Output
	-> NOTHING	: no permission found
	-> WARNING	: permission found
'''

class Rule10(Rules):
	def __init__(self, directory, database, verbose=True, verboseDeveloper=False, storeManager=None, flowdroid=False, platform="",validation=False, quiet=True):
		Rules.__init__(self, directory, database, verbose, verboseDeveloper, storeManager, flowdroid, platform, validation, quiet)

		self.AndroidErrMsg = "permission(s) allow() access to all public directories on external storage"
		self.AndroidOkMsg = "There is no access to all public directories on external storage"
		self.AndroidText = "https://developer.android.com/topic/security/best-practices#external-storage"

		self.okMsg = "No permission allow access to all public directories on external storage"		
		self.errMsg = "Some permissions allow access to all public directories on external storage, which might be more access than what your app needs"
		self.category = R.CAT_4

		self.findXml()
		self.show(10, "Use scoped directory access")

	def getDangerousPermissions(self, xmlReader, permissions):
		prefix = "android.permission."
		blackList = ['READ_EXTERNAL_STORAGE',
					 'WRITE_EXTERNAL_STORAGE']
		blackList = [prefix + s for s in blackList]

		dangerousPermissions = []
		for p in permissions:
			for arg in p[XmlReader.ARGS]:
				if 'android:name=' in arg:
					value = xmlReader.getArgValue(arg)
					if value in blackList:
						dangerousPermissions.append(p)
					break

		return dangerousPermissions


	def run(self):
		self.loading()
		if self.manifest != None:
			xmlReader = XmlReader(self.manifest)

			permissions = xmlReader.getArgsTag("uses-permission")

			dangerousPermissions = self.getDangerousPermissions(xmlReader, permissions)

			NotIn = xmlReader.constructToken(dangerousPermissions)
			# Set log msg
			NotIn 	= Parser.setMsg(NotIn, R.WARNING, self.errMsg)

			self.updateWN(xmlReader.getFile(), NotIn)

			self.loading()
			xmlReader.close()

			self.store(10, self.AndroidOkMsg, self.AndroidErrMsg, self.AndroidText, self.category, True)
			self.display(XmlReader)
		else:
			self.loading()


