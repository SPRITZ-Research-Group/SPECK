#!/usr/bin/python3

from Rules import *
from FileReader import *
from Parser import *
from R import *
import sys


'''
RULE N°26

+ SSLSocket 
** SSLSocket does not perform hostname verification. It is up to your app to do its own hostname verification, preferably by calling getDefaultHostnameVerifier() with the expected hostname.
-> https://developer.android.com/training/articles/security-ssl#WarningsSslSocket

? Pseudo Code:
	1. Find SSLSocket and get SSLSession associated
	2. Get HostnameVerifier and check if getDefaultHostnameVerifier() is used
	3. Check all SSLSession are in 'verify' method argument from a HostnameVerifier

! Output
	-> NOTHING	: No SSLSocket found
	-> OK 		: SSLSocket is well implemented
	-> CRITICAL	: SSLSocket doesn't use ‘createSocket’ or doesn't check hostname
'''

class Rule26(Rules):
	def __init__(self, directory, database, verbose=True, verboseDeveloper=False, storeManager=None, flowdroid=False, platform="",validation=False, quiet=True):
		Rules.__init__(self, directory, database, verbose, verboseDeveloper, storeManager, flowdroid, platform, validation, quiet)

		self.AndroidErrMsg = "SSLSocket (don't) perform() hostname verification"
		self.AndroidOkMsg = "SSLSocket perform() hostname verification"
		self.AndroidText = "https://developer.android.com/training/articles/security-ssl#WarningsSslSocket"

		self.okMsg = "SSLSocket performs hostname verification"
		self.errMsg = "SSLSocket does not perform hostname verification"
		self.errMsg2 = "Don't use custom hostname verifier"
		self.category = R.CAT_2
		
		self.filter('javax.net.ssl.SSLSocket')
		self.show(26, "SSLSocket")

	def checkSslSession(self, s, sslSession):
		for elem in sslSession:
			if s[R.VALUE] == elem[R.VALUE]:
				if elem[R.SCOPE] == R.VARGLOBAL:
					return elem
				elif elem[R.SCOPE] == R.VARCLASS and elem[R.CLASSID] == s[R.CLASSID]:
					return elem
				elif elem[R.SCOPE] == R.VARLOCAL and elem[R.CLASSID] == s[R.CLASSID] and elem[R.FUNCID] == s[R.FUNCID]:
					return elem
		return None

	def checkIfVerifyIsCalled(self, fileReader, host, sslSession):
		In = []
		NotIn = []

		for h in host:
			sslSessionArg = Parser.finder(fileReader, 
								[[Parser.findArgName, (h[R.VALUE] + '.verify', 1, None)]], True)[0]
			
			for s in sslSessionArg:
				session = self.checkSslSession(s, sslSession)
				if session != None:
					In.append(session)

		for elem in sslSession:
			if elem not in In:
				NotIn.append(elem)

		return In, NotIn

	def run(self):
		self.loading()

		for f in self.javaFiles:
			fileReader = FileReader(f)

			found = Parser.finder(fileReader, 
								[[Parser.findVarName, (['SSLSocket '], None)],
								 [Parser.findVarName, (['(SSLSocket)'], None)],# needed if socket is create but not assigned to a var. May cause the issue to be reported twice, but at least it is not ignored
								 [Parser.findVarName, (['SSLSession '], None)],
								 [Parser.findVarName, (['getSession()'], None)],
								 [Parser.findObjName, ('getSession', None)],
								 [Parser.findVarName, (['HostnameVerifier '], None)],
								 [Parser.findVarName, (['HttpsURLConnection.getDefaultHostnameVerifier'], None)],
								])

			sslSocket = found[0] + found[1]
			sslSession = found[2]
			getSessionName = found[3]
			getSessionObj = found[4]
			hostnameVerifier = found[5]
			defaultHostnameVerifier = found[6]

			# here it sets the scopes of the variables (i.e. whether they are local, global, class var => look at R.py)
			sslSocket = Parser.setScopes(sslSocket)
			sslSession = Parser.setScopes(sslSession)
			hostnameVerifier = Parser.setScopes(hostnameVerifier)

			# get SSLSocket which call and don't call getSession method
			tmp, NotIn = Parser.diff(sslSocket, getSessionObj)

			# get HostnameVerifier which call or not call 'getDefaultHostnameVerifier'
			host, NotIn2 = Parser.diff(hostnameVerifier, defaultHostnameVerifier)

			In, NotIn3 = self.checkIfVerifyIsCalled(fileReader, host, sslSession)

			In = Parser.setMsg(In, R.OK)
			NotIn = Parser.setMsg(NotIn + NotIn3, R.CRITICAL, self.errMsg)
			NotIn2 = Parser.setMsg(NotIn2, R.CRITICAL, self.errMsg2)

			self.updateOCN(f, In, NotIn + NotIn2, (len(In) == 0 and len(NotIn + NotIn2) == 0))
			self.loading()
			fileReader.close()

		self.store(26, self.AndroidOkMsg, self.AndroidErrMsg, self.AndroidText, self.category, False, [self.errMsg])
		self.display(FileReader)

