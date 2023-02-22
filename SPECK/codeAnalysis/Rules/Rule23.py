#!/usr/bin/python3

from Rules import *
from XmlReader import *
from Parser import *
from R import *
import sys


'''
RULE N°23

+ Use broadcast receivers
** Use android:permission attribute in broadcast receiver
-> https://developer.android.com/training/articles/security-tips#BroadcastReceivers

? Pseudo Code:
	1. If there is a receiver, suggest to protect it with android:permission attribute

! Output
	-> NOTHING	: no broadcast receiver found
	-> OK 	   	: a broadcast receiver use android:permission attribute
	-> WARNING	: a broadcast receiver doesn't use android:permission attribute
'''

class Rule23(Rules):
	def __init__(self, directory, database, verbose=True, verboseDeveloper=False, storeManager=None, flowdroid=False, platform="",validation=False, quiet=True):
		Rules.__init__(self, directory, database, verbose, verboseDeveloper, storeManager, flowdroid, platform, validation, quiet)

		self.AndroidErrMsg = "broadcast receiver(s) (are) not protected with a permission attribute"
		self.AndroidOkMsg = "broadcast receiver(s) (are) protected with a permission attribute"
		self.AndroidText = "https://developer.android.com/training/articles/security-tips#BroadcastReceivers"

		self.okMsg = "Broadcast receiver is well implemented"
		self.errMsg = "It's better to use android:permission attribute in a broadcast receiver"
		self.category = R.CAT_1
		
		self.findXml()
		self.show(23, "Use broadcast receivers")

	def checkReceivers(self, receivers):
		In = []
		NotIn = []

		for r in receivers:
			isIn = not self.is_exported(r)
			for arg in r[XmlReader.ARGS]:
				if 'android:permission' in arg:
					isIn = True
					break
			if isIn:
				In.append(r)
			else:
				NotIn.append(r)

		return In, NotIn
	
	@staticmethod
	def is_exported(receiver):
		for arg in receiver[XmlReader.ARGS]:
			if 'android:exported="false"' in arg:
				return False
			if 'android:exported="true"' in arg:
				return True
		if '<intent-filter>' in receiver[XmlReader.INSTR]:
			return True
		return False

	def run(self):
		self.loading()

		if self.manifest != None:
			xmlReader = XmlReader(self.manifest)

			receivers = xmlReader.getArgsTag("receiver")

			In, NotIn = self.checkReceivers(receivers)
			

			# format data to be display in 'Display' class
			In = xmlReader.constructToken(In)
			NotIn = xmlReader.constructToken(NotIn)

			# set log message
			In = Parser.setMsg(In, R.OK)
			NotIn = Parser.setMsg(NotIn, R.WARNING, self.errMsg)

			self.updateOWN(xmlReader.getFile(), In, NotIn, (len(receivers) == 0))

			xmlReader.close()
			self.loading()

			self.store(23, self.AndroidOkMsg, self.AndroidErrMsg, self.AndroidText, self.category)
			self.display(XmlReader)

		else:
			self.loading()
