#!/usr/bin/python3

from Rules import *
from FileReader import *
from Parser import *
from R import *
import sys, os

'''
RULE N°7

+ Use WebView objects carefully
** Load only whitelisted content in WebView objects
-> https://developer.android.com/topic/security/best-practices#webview
-> https://www.androidauthority.com/working-with-webview-736873/

? Pseudo Code:
	1. Get all WebViews
	2. Get all WebViews which use 'setWebViewClient' method
	3. Compare
	4. Check for all WebViews got in step 2, 
		if the argument given is an object which override the 'shouldOverrideUrlLoading' method

! Output
	-> NOTHING	: no webview found
	-> OK 	   	: webview used carefully
	-> CRITICAL	: webview not used carefully
'''

class Rule7(Rules):
	def __init__(self, directory, database, verbose=True, verboseDeveloper=False, storeManager=None, flowdroid=False, platform="",validation=False, quiet=True):
		Rules.__init__(self, directory, database, verbose, verboseDeveloper, storeManager, flowdroid, platform, validation, quiet)

		self.AndroidErrMsg = "webview(s) (don't) always load whitelisted content"
		self.AndroidOkMsg = "webview(s) (are) secure"
		self.AndroidText = "https://developer.android.com/topic/security/best-practices#webview"

		self.okMsg = "Webviews are used carefully with a website whitelist"		
		self.errMsg1 = "'setWebViewClient' method is not called"
		self.errMsg2 = "'setWebViewClient' argument object doesn't override 'shouldOverrideUrlLoading' method"
		self.category = R.CAT_2
		
		self.filter('android.webkit.WebView')
		self.show(7, "Load only whitelisted content in WebView objects")

	@staticmethod
	def seekCondsInFiles(javaFiles, conds):
		res = False

		for f in javaFiles:
			fileReader = FileReader(f)

			booleans = [False]*len(conds)

			line, elem = fileReader.getNextInstruction()
			clssID = fileReader.getClassID()
			constraintID = -1
			while(line != ''):
				if len([b for b in booleans if b is True]) == len(conds):
					res = True
					break

				if constraintID == -1 and all(word in line for word in conds[0]):
					constraintID = clssID
					booleans[0] = True

				for i in range(1, len(conds)):
					if all(word in line for word in conds[i]) and constraintID == clssID:
						booleans[i] = True

				line, elem = fileReader.getNextInstruction()
				clssID = fileReader.getClassID()

			fileReader.close()

			if res:
				break

		return res

	@staticmethod
	def getObjType(webviewsClasses, fileReader):
		webviewsClasses = Parser.setScopes(webviewsClasses)
		classNames = []

		request = []
		for w in webviewsClasses:
			request.append([Parser.findTypeVar, ([w[R.VALUE]+' ', 'new'], None)])
		
		found = Parser.finder(fileReader, request)

		index = 0
		for w in webviewsClasses:
			clssT = found[index]
			index += 1
			clssT = Parser.setScopes(clssT)

			# Delete useless clssT
			copy = clssT
			for c in copy:
				if c[R.SCOPE] == R.VARGLOBAL:
					pass
				elif c[R.SCOPE] == R.VARCLASS and c[R.CLASSID] == w[R.CLASSID]:
					pass
				elif c[R.SCOPE] == R.VARLOCAL and c[R.CLASSID] == w[R.CLASSID] and c[R.FUNCID] == w[R.FUNCID]:
					pass
				else:
					clssT.remove(c)

			classNames = classNames + clssT

		return classNames

	@staticmethod
	def checkClientImplementation(javaFiles, objT, fileReader):
		In = []
		NotIn = []

		# Check if 'shouldOverrideUrlLoading' is implemented
		for elem in objT:
			if Rule7.seekCondsInFiles(javaFiles, [ [" "+elem[R.VALUE]+" ", 'class'], [' shouldOverrideUrlLoading'] ]):
				In.append(elem)
			elif Rule7.seekCondsInFiles(javaFiles, [ [elem[R.VALUE], 'new', 'this'], [' shouldOverrideUrlLoading'] ]):
				In.append(elem)
			else:
				NotIn.append(elem)

		return In, NotIn

	@staticmethod
	def customFinder(fileReader, notFound):
		# GOAL: analyse function -> new MyClass(){ myFunction(){ ... } ... }
		In = []
		NotIn = []
		NotIn2 = []

		for elem in notFound:
			line, tok = fileReader.getNextInstruction()
			setWebViewClientWasFound = False
			shouldOverrideUrlLoadingWasFound = False
			while line != '':
				line = ' '.join(line.split()).strip()
				
				if elem[R.VALUE]+".setWebViewClient" in line and 'new' in line:
					setWebViewClientWasFound = True
					bId = tok[R.BLOCKID]
					line, tok = fileReader.getNextInstruction()
					while (tok[R.BLOCKID] > bId):
						if ("shouldOverrideUrlLoading" in line):
							shouldOverrideUrlLoadingWasFound = True
							break
						line, tok = fileReader.getNextInstruction()
					
					if shouldOverrideUrlLoadingWasFound:
						break

				line, tok = fileReader.getNextInstruction()

			if not setWebViewClientWasFound:
				NotIn.append(elem)
			elif not shouldOverrideUrlLoadingWasFound:
				NotIn2.append(elem)
			else:
				In.append(elem)

			fileReader.resetCursor()

		return In, NotIn, NotIn2

	
	def run(self):
		self.loading()
		
		for f in self.javaFiles:
			fileReader = FileReader(f)

			found = Parser.finder(fileReader, 
								[[Parser.findVarName, (['WebView '], None)],
								 [Parser.findObjName, ('setWebViewClient', None)],
								 [Parser.findArgName, ('setWebViewClient', 0, None)]
								])

			webviews 			= found[0]
			setWebViewClients 	= found[1]
			webviewsClasses 	= found[2]
			
			cpy = webviews.copy()
			for w in cpy:
				if not w[R.INSTR].startswith('WebView '):
					webviews.remove(w)

			webviews = Parser.setScopes(webviews)

			# webviews have to use 'setWebViewClients' method
			In, NotIn = Parser.diff(webviews, setWebViewClients)
			
			# Check if 'setWebViewClient' argument is an object which override the 'shouldOverrideUrlLoading' method
			if len(In) != 0:
				objT = Rule7.getObjType(webviewsClasses, fileReader)
				In, NotIn2 = Rule7.checkClientImplementation(self.javaFiles, objT, fileReader)

			# if no 'WebView' were found
			else:
				NotIn2 = []

			# Update Parser.VALUE field
			for e in In:
				e[R.VALUE] = e[R.EXTRA][0][0]
			for e in NotIn2:
				e[R.VALUE] = e[R.EXTRA][0][0]

			# VERY PARTICULAR CASE !
			newIn, newNotIn, newNotIn2 = Rule7.customFinder(fileReader, NotIn)
			In = In + newIn
			NotIn = newNotIn
			NotIn2 = NotIn2 + newNotIn2

			# Set log msg
			In = Parser.setMsg(In, R.OK)
			NotIn = Parser.setMsg(NotIn, R.CRITICAL, self.errMsg1)
			NotIn2 = Parser.setMsg(NotIn2, R.CRITICAL, self.errMsg2)

			NotIn = NotIn + NotIn2

			self.updateOCN(f, In, NotIn, (len(webviews) == 0 or (len(NotIn) == 0 and len(In) == 0)))
			self.loading()
			fileReader.close()

		self.store(7, self.AndroidOkMsg, self.AndroidErrMsg, self.AndroidText, self.category, False, [self.errMsg1])
		self.display(FileReader)




