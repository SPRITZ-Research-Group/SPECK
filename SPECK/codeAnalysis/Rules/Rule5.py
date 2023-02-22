#!/usr/bin/python3

from Rules import *
from FileReader import *
from Parser import *
from R import *
from Common import *


'''
RULE N°5

+ Use SSL Traffic
** Use HTTPS and manage unknown certificates
-> https://developer.android.com/topic/security/best-practices#network
-> https://developer.android.com/training/articles/security-ssl

? Pseudo Code:
	1. Get all var which use 'openConnection'
	2. Get all 'HttpsURLConnection' var which use 'openConnection' method
	3. Get all 'HttpsURLConnection' which use 'setSSLSocketFactory' method
	4. Compare step 1 & 2
	5. Compare step 2 & 3
	6. For issues found in step 5, 
		check if 'openConnection' method is called in a try/catch (to catch 'SSLHandshakeException')

! Output
	-> NOTHING	: no 'openConnection' found
	-> OK 	   	: https good pratice
	-> CRITICAL	: https bad pratice
'''

class Rule5(Rules):
	def __init__(self, directory, database, verbose=True, verboseDeveloper=False, storeManager=None, flowdroid=False, platform="",validation=False, quiet=True):
		Rules.__init__(self, directory, database, verbose, verboseDeveloper, storeManager, flowdroid, platform, validation, quiet)

		self.AndroidErrMsg = "connection(s) (are) not secure"
		self.AndroidOkMsg = "connection(s) (are) secure"
		self.AndroidText = "https://developer.android.com/topic/security/best-practices#network"
		
		self.okMsg = "Some open connections are secure"		
		self.errMsg1 = "HTTPS connection is not used"
		self.errMsg2 = "'SSLHandshakeException' is not managed (with 'TrustManager' or 'try/catch')"
		self.category = R.CAT_2
		
		self.filter('java.net.URL')
		self.show(5, "Use SSL traffic")

	def remove_trycatch(self, NotIn): # if in the try/catch block, it means that it's ok
		In = []

		copy = NotIn
		for c in copy:
			if c[R.INTRY]:
				In.append(c)
				NotIn.remove(c)

		return In, NotIn

	def run(self):
		####################################################################################################
		#                                             Standard                                             #
		####################################################################################################
		self.loading()
		####################################################################################################
		#                                           End Standard                                           #
		####################################################################################################
		
		for f in self.javaFiles:
			fileReader = FileReader(f)

			# Get all variables which use 'openConnection' method
			openConnections = Common.get_all_var_names(fileReader, ['.openConnection('])
			# Get all variables names which are 'HttpsURLConnection'

			httpVars = Common.get_all_var_names(fileReader, ['HttpsURLConnection '])
			# Get all variables which use 'setSSLSocketFactory'
			varWithSocketFactory = Common.get_all_obj_names(fileReader, 'setSSLSocketFactory')

			# Set scope for variable declared with https
			# Check if all 'openConnection' method used are for an 'HttpsURLConnection' variable
			In, NotIn = Common.compare(httpVars, openConnections, reverse=True)

			####################################################################################################
			#                                             Standard                                             #
			####################################################################################################
			# Set log msg
			NotIn = Parser.setMsg(NotIn, R.CRITICAL, self.errMsg1)
			####################################################################################################
			#                                           End Standard                                           #
			####################################################################################################
			
			# Check if all 'HttpsURLConnection' variables call 'setSSLSocketFactory' method: a TrustManager must be used !
			In, NotIn2 = Common.compare(In, varWithSocketFactory)

			########################################
			#               SPECIFIC               #
			########################################
			# Check if variables which call 'openConnection' is done in a 'try{}catch{}'
			In2, NotIn2 = self.remove_trycatch(NotIn2)
			########################################
			#             END SPECIFIC             #
			########################################

			In = In + In2
			In = Parser.setMsg(In, R.OK)
			NotIn2 = Parser.setMsg(NotIn2, R.CRITICAL, self.errMsg2)
			NotIn = NotIn + NotIn2

			self.updateOCN(f, In, NotIn, (len(openConnections) == 0))
			# self.just_update(f, NotIn, R.CRITICAL)
			self.loading()
			fileReader.close()

		self.store(5, self.AndroidOkMsg, self.AndroidErrMsg, self.AndroidText, self.category)
		self.display(FileReader)

