#!/usr/bin/python3

from Rules import *
from FileReader import *
from Parser import *
from R import *
from Common import *
import sys


'''
RULE N°6

+ Use HTML message channels
** If your app must use JavaScript, use HTML message channels instead of evaluateJavascript(), ...
-> https://developer.android.com/topic/security/best-practices#webview

? Pseudo Code:
	1. Look for particular keywords which have security issues

! Output
	-> NOTHING	: no depreciated function found
	-> CRITICAL	: depreciated function found
'''

class Rule6(Rules):
	def __init__(self, directory, database, verbose=True, verboseDeveloper=False, storeManager=None, flowdroid=False, platform="",validation=False, quiet=True):
		Rules.__init__(self, directory, database, verbose, verboseDeveloper, storeManager, flowdroid, platform, validation, quiet)

		self.AndroidErrMsg = "deprecated function(s) (are) used"
		self.AndroidOkMsg = "no depreciated Javascript function is used"
		self.AndroidText = "https://developer.android.com/topic/security/best-practices#webview"

		self.okMsg = "No javascript function deprecated is used"
		self.errMsg = "evaluateJavascript(), addJavascriptInterface() or setJavaScriptEnabled() are used but deprecated"
		self.category = R.CAT_2
		
		self.filter('android.webkit.WebView')
		self.show(6, "Use HTML message channels")

	def run(self):
		self.loading()

		for f in self.javaFiles:
			fileReader = FileReader(f)

			# Look for depreciated functions
			found = Common.search_keywords(fileReader, ['.evaluateJavascript', '.addJavascriptInterface', '.setJavaScriptEnabled(true)'])

			# Set log msg
			found = Parser.setMsg(found, R.CRITICAL, self.errMsg)

			self.updateCN(f, found)
			self.loading()
			fileReader.close()

		self.store(6, self.AndroidOkMsg, self.AndroidErrMsg, self.AndroidText, self.category, True)
		self.display(FileReader)
