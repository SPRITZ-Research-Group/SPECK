#!/usr/bin/python3

from Rules import *
from XmlReader import *
from Parser import *
from R import *
from Common import *
import sys


'''
RULE N°27

+ Configure CAs for debugging
** Normally, IDEs and build tools set this flag automatically for non-release builds
-> https://developer.android.com/training/articles/security-config#TrustingDebugCa

? Pseudo Code:
	1. Look for ‘android:networkSecurityConfig’ in manifest file
	2. Look for <network-security-config> and <debug-overrides> in networking security configuration file 

! Output
	-> NOTHING	: No security config file found or no <debug-overrides> tag found
	-> WARNING	: <debug-overrides> tag found
'''

class Rule27(Rules):
	def __init__(self, directory, database, verbose=True, verboseDeveloper=False, storeManager=None, flowdroid=False, platform="",validation=False, quiet=True):
		Rules.__init__(self, directory, database, verbose, verboseDeveloper, storeManager, flowdroid, platform, validation, quiet)

		self.AndroidErrMsg = "tag(s) found in networking security file"
		self.AndroidOkMsg1 = "no debug tag found in networking security file"
		self.AndroidOkMsg2 = "no networking security file found"
		self.AndroidOkMsg = self.AndroidOkMsg1
		self.AndroidText = "https://developer.android.com/training/articles/security-config#TrustingDebugCa"

		self.okMsg = "no <debug-overrides> tag found in networking security file"
		self.errMsg = "don't forget to disable <debug-overrides> in networking security file"
		self.category = R.CAT_2
		
		self.findXml()
		self.show(27, "Configure CAs for debugging")

	def getNetworkFile(self, app, xmlReader):
		for tag in app:
			args = tag[XmlReader.ARGS]
			index, value = Common.get_arg_index_and_value(args, "android:networkSecurityConfig")
			if index >= 0:
				return Common.analyse_non_manifest_xml(self.manifest, value)
		return None, None

	def run(self):
		self.loading()

		if self.manifest != None:
			xmlReader = XmlReader(self.manifest)

			app = xmlReader.getArgsTag("application")

			debuggable = False
			for a in app:
				for arg in a[XmlReader.ARGS]:
					if 'android:debuggable="true"' in arg:
						debuggable = True

			if debuggable:
				securityConfigReader, networkFile = self.getNetworkFile(app, xmlReader)

				if (networkFile != None):
					self.maxFiles += 1
					#securityConfigReader = XmlReader(networkFile)

					debug = securityConfigReader.getArgsTag("debug-overrides")
					NotIn = xmlReader.constructToken(debug)

					# Set log msg
					NotIn = Parser.setMsg(NotIn, R.WARNING, self.errMsg)

					self.updateWN(networkFile, NotIn)
					securityConfigReader.close()
				else: 
					self.AndroidOkMsg = self.AndroidOkMsg2
					self.updateWN(self.manifest, [])
			else: 
				self.updateWN(self.manifest, [])

			xmlReader.close()
			self.loading()

			self.store(27, self.AndroidOkMsg, self.AndroidErrMsg, self.AndroidText, self.category)
			self.display(XmlReader)
