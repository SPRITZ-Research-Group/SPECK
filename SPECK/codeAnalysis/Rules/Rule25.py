#!/usr/bin/python3

from Rules import *
from FileReader import *
from Parser import *
from R import *
import sys


'''
RULE N°25

+ Hostname verification
** Replacing HostnameVerifier can be very dangerous if the other virtual host is not under your control, because a man-in-the-middle attack could direct traffic to another server without your knowledge.
-> https://android-doc.github.io/training/articles/security-ssl.html#CommonHostnameProbs

? Pseudo Code:
	1. Look for 'HttpsUrlConnection'
	2. If ‘setHostnameVerifier’ is found, discourage its use 

! Output
	-> NOTHING	: No 'HttpsUrlConnection' found
	-> CRITICAL	: 'HttpsUrlConnection' call ‘setHostnameVerifier’
'''

class Rule25(Rules):
	def __init__(self, directory, database, verbose=True, verboseDeveloper=False, storeManager=None, flowdroid=False, platform="",validation=False, quiet=True):
		Rules.__init__(self, directory, database, verbose, verboseDeveloper, storeManager, flowdroid, platform, validation, quiet)

		self.AndroidErrMsg = "Https connection(s) might be subject to a man-in-the-middle attack"
		self.AndroidOkMsg = "Https connection(s) (are) not subject to a man-in-the-middle attack"
		self.AndroidText = "https://developer.android.com/training/articles/security-ssl#CommonHostnameProbs"

		self.okMsg = "HostnameVerifier is not replaced"
		self.errMsg = "Replacing HostnameVerifier can be very dangerous if the other virtual host is not under your control"
		self.category = R.CAT_2
		
		self.filter('java.net.URL')
		self.show(25, "Hostname verification")

	def run(self):
		self.loading()

		for f in self.javaFiles:
			fileReader = FileReader(f)

			found = Parser.finder(fileReader, 
								[[Parser.findVarName, (['HttpsURLConnection '], None)],
								 [Parser.findObjName, ('setHostnameVerifier', None)],
								 [Parser.findObjName, ('setDefaultHostnameVerifier', None)],
								])

			httpsVars = found[0]
			hostnameVerifier = found[1]

			httpsVars = Parser.setScopes(httpsVars)
			NotIn, In = Parser.diff(httpsVars, hostnameVerifier)
			NotIn += found[2]
			# Set log msg
			In = Parser.setMsg(In, R.OK)
			NotIn = Parser.setMsg(NotIn, R.CRITICAL, self.errMsg)

			self.updateOCN(f, In, NotIn, (len(In) == 0 and len(NotIn) == 0))
			self.loading()
			fileReader.close()

		self.store(25, self.AndroidOkMsg, self.AndroidErrMsg, self.AndroidText, self.category, False, [self.errMsg])
		self.display(FileReader)









