#!/usr/bin/python3

from Rules import *
from FileReader import *
from Parser import *
from R import *
import sys


'''
RULE N°29

+ Choose a recommended algorithm
-> https://developer.android.com/guide/topics/security/cryptography#choose-algorithm

? Pseudo Code:
	1. Check ‘getInstance’ argument for each cryptographic class and compare with recommendation 

! Output
	-> NOTHING	: no cryptographic class found
	-> WARNING	: a cryptographic class doesn't use an algorithm recommended
	-> OK  		: a cryptographic class use an algorithm recommended
'''

class Rule29(Rules):
	def __init__(self, directory, database, verbose=True, verboseDeveloper=False, storeManager=None, flowdroid=False, platform="",validation=False, quiet=True):
		Rules.__init__(self, directory, database, verbose, verboseDeveloper, storeManager, flowdroid, platform, validation, quiet)

		self.AndroidErrMsg = "cryptographic algorithm(s) not recommended (are) used"
		self.AndroidOkMsg = "cryptographic algorithm(s) recommended (are) used"
		self.AndroidText = "https://developer.android.com/guide/topics/security/cryptography#choose-algorithm"

		self.okMsg = "A recommended cryptographic algorithm is used"
		self.errMsg = "It's better to use a recommended cryptographic algorithm"
		self.category = R.CAT_5
		
		self.filters(['javax.crypto.Cipher', 'java.security.MessageDigest', 'javax.crypto.Mac', 'java.security.Signature'])
		self.show(29, "Choose a recommended algorithm")

	def checkCryptoArg(self, args, conds):
		In = []
		NotIn = []

		for arg in args:
			checked = False
			for c in conds:
				if all(e in arg[R.VALUE] for e in c):
					In.append(arg)
					checked = True
					break

			if not checked:
				NotIn.append(arg)

		return In, NotIn

	def run(self):
		self.loading()

		for f in self.javaFiles:
			fileReader = FileReader(f)

			found = Parser.finder(fileReader, 
								[[Parser.findArgName, ('Cipher.getInstance', 0, None)],
								 [Parser.findArgName, ('MessageDigest.getInstance', 0, None)],
								 [Parser.findArgName, ('Mac.getInstance', 0, None)],
								 [Parser.findArgName, ('Signature.getInstance', 0, None)]
								 ])

			cipher = found[0]
			message = found[1]
			mac = found[2]
			sign = found[3]

			In, NotIn = self.checkCryptoArg(cipher, [['AES', 'CBC'], ['AES', 'GCM']])

			tmp1, tmp2 = self.checkCryptoArg(message, [['SHA-2'], ['SHA2']])
			In += tmp1
			NotIn += tmp2

			tmp1, tmp2 = self.checkCryptoArg(mac, [['SHA-2', 'HMAC'], ['SHA2', 'HMAC']])
			In += tmp1
			NotIn += tmp2

			tmp1, tmp2 = self.checkCryptoArg(sign, [['SHA-2', 'ECDSA'], ['SHA2', 'ECDSA']])
			In += tmp1
			NotIn += tmp2

			# Set log msg
			In = Parser.setMsg(In, R.OK)
			NotIn = Parser.setMsg(NotIn, R.WARNING, self.errMsg)

			self.updateOWN(f, In, NotIn, (len(NotIn) == 0 and len(In) == 0))
			self.loading()
			fileReader.close()

		self.store(29, self.AndroidOkMsg, self.AndroidErrMsg, self.AndroidText, self.category, True)
		self.display(FileReader)







		

