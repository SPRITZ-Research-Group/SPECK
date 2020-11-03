#!/usr/bin/python3

from Rules import *
from FileReader import *
from Parser import *
from R import *
import sys


'''
RULE N°16

+ Delete files stored locally with a WebView
-> https://developer.android.com/training/articles/security-tips#WebView

? Pseudo Code:
	1. Look for ‘clearCache’ methods

! Output
	-> NOTHING	: no 'webview' method found
	-> OK 		: webview use 'clearCache' method
	-> WARNING	: webview doesn't use 'clearCache' method
'''

class Rule16(Rules):
	def __init__(self, directory, database, verbose=True, verboseDeveloper=False, storeManager=None, flowdroid=False, platform="",validation=False, quiet=True):
		Rules.__init__(self, directory, database, verbose, verboseDeveloper, storeManager, flowdroid, platform, validation, quiet)

		self.AndroidErrMsg = "webview(s) (don't) delete files stored locally"
		self.AndroidOkMsg = "webview(s) delete() files stored locally"
		self.AndroidText = "https://developer.android.com/training/articles/security-tips#WebView"

		self.okMsg = "Webview delete files stored locally"
		self.errMsg = "Each webview has to delete files stored locally with 'clearCache'"
		self.category = R.CAT_2
		
		self.filter('android.webkit.WebView')
		self.show(16, "Delete files stored locally with a WebView")

	def run(self):
		self.loading()
		
		for f in self.javaFiles:
			fileReader = FileReader(f)

			found = Parser.finder(fileReader, 
								[[Parser.findVarName, (['WebView '], None)],
								 [Parser.findObjName, ('clearCache', None)]])

			webviews = found[0]
			webviewsClearCache = found[1]

			cpy = webviews.copy()
			for w in cpy:
				if not w[R.INSTR].startswith('WebView '):
					webviews.remove(w)

			webviews = Parser.setScopes(webviews)

			# webviews have to use 'clearCache' method
			In, NotIn = Parser.diff(webviews, webviewsClearCache)

			# Set log msg
			In 		= Parser.setMsg(In, R.OK)
			NotIn 	= Parser.setMsg(NotIn, R.WARNING, self.errMsg)

			self.updateOWN(f, In, NotIn, (len(webviews) == 0))
			self.loading()
			fileReader.close()

		self.store(16, self.AndroidOkMsg, self.AndroidErrMsg, self.AndroidText, self.category)
		self.display(FileReader)


