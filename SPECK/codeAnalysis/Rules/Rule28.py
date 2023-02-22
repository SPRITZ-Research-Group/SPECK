#!/usr/bin/python3

from Rules import *
from XmlReader import *
from Parser import *
from R import *
from Common import *
import sys
from os import path


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

	def run(self):
		self.loading()

		if self.manifest != None:
			xmlReader = XmlReader(self.manifest)

			application = Common.get_xml_tag_args(xmlReader, 'application')

			for app in application:
				args = app[XmlReader.ARGS]
				index, value = Common.get_arg_index_and_value(args, "android:networkSecurityConfig")
				if index >= 0:
					# android:networkSecurityConfig="@xml/network_security_config">
					#networkFile = self.manifest.replace('AndroidManifest.xml', "res/") + value.replace('@', "") + ".xml"
					#print(networkFile)
					self.maxFiles += 1
					networkFileReader, networkFile = Common.analyse_non_manifest_xml(self.manifest, value)

					domain = Common.get_xml_tag_args(networkFileReader, 'domain-config')
					domain += Common.get_xml_tag_args(networkFileReader, 'base-config')
					NotIn = []
					for d in domain: 
						args = d[XmlReader.ARGS]
						dIndex, dValue = Common.get_arg_index_and_value(args, 'cleartextTrafficPermitted')
						if dIndex >= 0:
							if dValue == "true":
								NotIn.append(d)

					NotIn = xmlReader.constructToken(NotIn)

					# Set log msg
					NotIn 	= Parser.setMsg(NotIn, R.WARNING, self.errMsg)

					self.updateWN(networkFile, NotIn)
					networkFileReader.close()
				
			xmlReader.close()
			self.loading()

			self.store(28, self.AndroidOkMsg, self.AndroidErrMsg, self.AndroidText, self.category)
			self.display(XmlReader)





