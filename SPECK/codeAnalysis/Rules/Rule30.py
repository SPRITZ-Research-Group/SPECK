#!/usr/bin/python3

from Rules import *
from FileReader import *
from Parser import *
from R import *
import sys


'''
RULE N°30

+ Deprecated cryptographic functionality
** Requesting a specific provider is discouraged
** An explicit IV should always be passed when using PBE ciphers
-> https://developer.android.com/guide/topics/security/cryptography#deprecated-functionality

? Pseudo Code:
	1. Check the 2nd argument of ‘Cipher.getInstance’
	2. Look for ‘Cipher.getInstance("PBE…")’ and check if ‘cipher.init’ is called

! Output
	-> NOTHING	: No Cipher.getInstance found
	-> OK 		: Cipher.getInstance doesn't use a provider
	-> CRITICAL	: Cipher.getInstance had a bad argument or doesn't call 'init' method
'''

class Rule30(Rules):
	def __init__(self, directory, database, verbose=True, verboseDeveloper=False, storeManager=None, flowdroid=False, platform="",validation=False, quiet=True):
		Rules.__init__(self, directory, database, verbose, verboseDeveloper, storeManager, flowdroid, platform, validation, quiet)

		self.AndroidErrMsg = "deprecated cryptographic functionalit(ies) (are) used"
		self.AndroidOkMsg = "no deprecated cryptographic functionality is used"
		self.AndroidText = "https://developer.android.com/guide/topics/security/cryptography#deprecated-functionality"

		self.errMsg1 = "Don't use a provider with Cipher.getInstance()"
		self.errMsg2 = "When you use PBE, don't forget to call init() method on cipher object"
		self.category = R.CAT_5
		
		self.filter('javax.crypto.Cipher')
		self.show(30, "Deprecated cryptographic functionality")

	def run(self):
		self.loading()

		for f in self.javaFiles:
			fileReader = FileReader(f)

			found = Parser.finder(fileReader, 
								[[Parser.findArgName, ('Cipher.getInstance', 1, None)],
								 [Parser.findVarName, (['Cipher '], None)],
								 [Parser.findVarName, (['Cipher.getInstance("PBE'], None)],
								 [Parser.findObjName, ('init', None)]])

			NotIn = found[0]
			cipher = found[1]
			cipherPbe = found[2]
			cipherInit = found[3]

			cipher = Parser.setScopes(cipher)
			cipherPbe, other = Parser.diff(cipher, cipherPbe)

			In, NotIn2 = Parser.diff(cipherPbe, cipherInit)

			# Set log msg
			In = Parser.setMsg(In, R.OK)
			NotIn = Parser.setMsg(NotIn, R.CRITICAL, self.errMsg1)
			NotIn2 = Parser.setMsg(NotIn2, R.CRITICAL, self.errMsg2)

			self.updateOCN(f, In, NotIn + NotIn2, (len(NotIn + NotIn2) == 0 and len(In) == 0))
			self.loading()
			fileReader.close()

		self.store(30, self.AndroidOkMsg, self.AndroidErrMsg, self.AndroidText, self.category, True, [self.errMsg2])
		self.display(FileReader)







		

