#!/usr/bin/python3

from Rules import *
from XmlReader import *
from Parser import *
from R import *
import sys


'''
RULE N°28

+ Opt out of cleartext traffic
-> https://developer.android.com/training/articles/security-config#CleartextTrafficPermitted

? Pseudo Code:
	1. Check if ‘cleartextTrafficPermitted’ is set to true or not set in <domain-config> tag

! Output
	-> NOTHING	: No security config file found or no ‘cleartextTrafficPermitted’ true found
	-> WARNING	: ‘cleartextTrafficPermitted’ true found
'''

class Rule28(Rules):
	def __init__(self, directory, database, verbose=True, verboseDeveloper=False, storeManager=None, flowdroid=False, platform="",validation=False, quiet=True):
		Rules.__init__(self, directory, database, verbose, verboseDeveloper, storeManager, flowdroid, platform, validation, quiet)

		self.AndroidErrMsg = "clear text(s) permitted in networking security file"
		self.AndroidOkMsg1 = "no clear text permitted in networking security file"
		self.AndroidOkMsg2 = "no networking security file found"
		self.AndroidOkMsg = self.AndroidOkMsg1
		self.AndroidText = "https://developer.android.com/training/articles/security-config#CleartextTrafficPermitted"

		self.okMsg = "no clear text permitted in networking security file"
		self.errMsg = "Set cleartextTrafficPermitted to False"
		self.category = R.CAT_2
		
		self.findXml()
		self.show(28, "Opt out of cleartext traffic")

	def getNetworkFile(self, app, xmlReader):
		for tag in app:
			for arg in tag[XmlReader.ARGS]:
				if "android:networkSecurityConfig" in arg:
					return self.manifest.replace("AndroidManifest.xml", "") + xmlReader.getArgValue(arg).replace("@", "") + ".xml"
		return None

	def getBadDom(self, domain, reader):
		NotIn = []

		for tag in domain:
			found = False
			for arg in tag[XmlReader.ARGS]:
				if "cleartextTrafficPermitted" in arg:
					found = True
					value = reader.getArgValue(arg)

					if value == "true":
						NotIn.append(tag)
					break

			if not found:
				NotIn.append(tag)

		return NotIn

	def run(self):
		self.loading()

		if self.manifest != None:
			xmlReader = XmlReader(self.manifest)

			app = xmlReader.getArgsTag("application")
			networkFile = self.getNetworkFile(app, xmlReader)

			if (networkFile != None):
				self.maxFiles += 1
				securityConfigReader = XmlReader(networkFile)

				domain = securityConfigReader.getArgsTag("domain-config")
				badDom = self.getBadDom(domain, securityConfigReader)

				NotIn = xmlReader.constructToken(badDom)

				# Set log msg
				NotIn 	= Parser.setMsg(NotIn, R.WARNING, self.errMsg)

				self.updateWN(networkFile, NotIn)
				securityConfigReader.close()
			else : 
				self.AndroidOkMsg = self.AndroidOkMsg2
				self.updateWN(self.manifest, [])

			xmlReader.close()
			self.loading()

			self.store(28, self.AndroidOkMsg, self.AndroidErrMsg, self.AndroidText, self.category)
			self.display(XmlReader)





