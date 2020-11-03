#!/usr/bin/python3

from Rules import *
from XmlReader import *
from Parser import *
from R import *
import sys


'''
RULE N°21

+ Use telephony networking
** SMS is neither encrypted nor strongly authenticated
** SMS messages are transmitted as broadcast intents, so they may be read or captured by other applications that have the READ_SMS permission
-> https://developer.android.com/training/articles/security-tips#IPNetworking

? Pseudo Code:
	1. Look for SEND_SMS permission
	2. Look for READ_SMS or RECEIVE_SMS


! Output
	-> NOTHING	: no permission found
	-> WARNING	: permission found
'''

class Rule21(Rules):
	def __init__(self, directory, database, verbose=True, verboseDeveloper=False, storeManager=None, flowdroid=False, platform="",validation=False, quiet=True):
		Rules.__init__(self, directory, database, verbose, verboseDeveloper, storeManager, flowdroid, platform, validation, quiet)

		self.AndroidErrMsg = "permission(s) for SMS (are) used. However SMS is not a secure protocol"
		self.AndroidOkMsg = "no SMS is sent or read"
		self.AndroidText = "https://developer.android.com/training/articles/security-tips#IPNetworking"

		self.errMsg = "Don't use SMS protocol. SMS content is not encrypted nor strongly authenticated and SMS are transmitted as broadcast intents so anyone can read them"
		self.errMsg2 = "Don't use SMS protocol. A malicious user may have sent the SMS to your application"
		self.category = R.CAT_2
		
		self.findXml()
		self.show(21, "Use telephony networking")

	def searchSms(self, permissions):
		NotIn = []
		NotIn2 = []
		for p in permissions:
			for arg in p[XmlReader.ARGS]:
				if 'SEND_SMS' in arg:
					NotIn.append(p)
					break
				if ('READ_SMS' in arg) or ('RECEIVE_SMS' in arg):
					NotIn2.append(p)
					break

		return NotIn, NotIn2

	def run(self):
		self.loading()

		if self.manifest != None:
			xmlReader = XmlReader(self.manifest)

			permissions = xmlReader.getArgsTag("uses-permission")
			NotIn, NotIn2 = self.searchSms(permissions)
			

			# format data to be display in 'Display' class
			NotIn = xmlReader.constructToken(NotIn)
			NotIn2 = xmlReader.constructToken(NotIn2)

			# set log message
			NotIn = Parser.setMsg(NotIn, R.WARNING, self.errMsg)
			NotIn2 = Parser.setMsg(NotIn2, R.WARNING, self.errMsg2)
			NotIn = NotIn + NotIn2

			self.updateWN(xmlReader.getFile(), NotIn)

			xmlReader.close()
			self.loading()

			self.store(21, self.AndroidOkMsg, self.AndroidErrMsg, self.AndroidText, self.category, True)
			self.display(XmlReader)

		else:
			self.loading()



