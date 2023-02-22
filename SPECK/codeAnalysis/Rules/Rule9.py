#!/usr/bin/python3

from Rules import *
from FileReader import *
from Parser import *
from R import *
import sys


'''
RULE N°9

+ Share data securely across apps
** share your app's content with other apps in a more secure manner
-> https://developer.android.com/topic/security/best-practices#permissions-share-data

? Pseudo Code:
	1. Look for intents which share data by calling 'setData' method
	2. Check argument
	3. Look for a call to 'addFlags'
	4. Check argument

! Output
	-> NOTHING	: no 'setData' method found
	-> OK 	   	: intent share data carefully
	-> CRITICAL	: intent share data not carefully
'''

class Rule9(Rules):
	def __init__(self, directory, database, verbose=True, verboseDeveloper=False, storeManager=None, flowdroid=False, platform="",validation=False, quiet=True):
		Rules.__init__(self, directory, database, verbose, verboseDeveloper, storeManager, flowdroid, platform, validation, quiet)

		self.AndroidErrMsg = "intent(s) which share data (don't) follow the good pratice"
		self.AndroidOkMsg = "intent(s) which share data follow() the good pratice"
		self.AndroidText = "https://developer.android.com/topic/security/best-practices#permissions-share-data"

		self.okMsg = "Data are shared securely"
		self.errMsg1 = "When sharing data, use 'content://' URI, not 'file://'"
		self.errMsg2 = "Provide clients one-time access to data by using the FLAG_GRANT_READ_URI_PERMISSION and FLAG_GRANT_WRITE_URI_PERMISSION flags"
		self.category = R.CAT_4
		
		self.filter('android.content.Intent')
		self.show(9, "Share data securely across apps")

	def findStringValue(self, fileReader, intent, value):
		found = Parser.finder(fileReader,
									[[Parser.findVarName, (['String '], None)]])
		string = Parser.setScopes(found[0])
		arg = None
		for s in string:
			if s[R.VALUE] == value:
				if ((s[R.SCOPE] == R.VARGLOBAL) or 
					(s[R.SCOPE] == R.VARCLASS and intent[R.CLASSID] == s[R.CLASSID]) or
					(s[R.SCOPE] == R.VARLOCAL and intent[R.CLASSID] == s[R.CLASSID] and intent[R.FUNCID] == s[R.FUNCID])):

					if '=' in s[R.INSTR]:
						arg = s[R.INSTR].split('=')[1].split(';')[0].strip()
					else:
						stringName = s[R.INSTR].split(';')[0].strip().split(' ')[-1]
						found2 = Parser.finder(fileReader,
								[[Parser.findLine, ([[stringName + '=']], None)],
								 [Parser.findLine, ([[stringName + ' =']], None)]])
						found2 = found2[0] + found2[1]

						for f in found2:
							if ((s[R.SCOPE] == R.VARGLOBAL) or 
								(s[R.SCOPE] == R.VARCLASS and f[R.CLASSID] == s[R.CLASSID]) or
								(s[R.SCOPE] == R.VARLOCAL and f[R.CLASSID] == s[R.CLASSID] and f[R.FUNCID] == s[R.FUNCID])):
								arg = f[R.INSTR].split('=')[1].split(';')[0]
								break

					arg = arg[1:len(arg)-1]
		return arg

	def findUriValue(self, fileReader, intent, value):
		found = Parser.finder(fileReader,
								[[Parser.findVarName, (['Uri '], None)]])

		uri = Parser.setScopes(found[0])
		arg = None

		for u in uri:
			if u[R.VALUE] == value:
				if ((u[R.SCOPE] == R.VARGLOBAL) or 
						(u[R.SCOPE] == R.VARCLASS and intent[R.CLASSID] == u[R.CLASSID]) or
						(u[R.SCOPE] == R.VARLOCAL and intent[R.CLASSID] == u[R.CLASSID] and intent[R.FUNCID] == u[R.FUNCID])):

					if '=' in u[R.INSTR]:
						if 'Uri.parse(' in u[R.INSTR]:
							arg = u[R.INSTR].split('Uri.parse(')[1].split(')')[0].strip()
					else:
						uriName = u[R.INSTR].split(';')[0].strip().split(' ')[-1]
						found2 = Parser.finder(fileReader,
								[[Parser.findLine, ([[uriName + '=']], None)],
								 [Parser.findLine, ([[uriName + ' =']], None)]])
						found2 = found2[0] + found2[1]

						for f in found2:
							if ((u[R.SCOPE] == R.VARGLOBAL) or 
								(u[R.SCOPE] == R.VARCLASS and f[R.CLASSID] == u[R.CLASSID]) or
								(u[R.SCOPE] == R.VARLOCAL and f[R.CLASSID] == u[R.CLASSID] and f[R.FUNCID] == u[R.FUNCID])):
								arg = f[R.INSTR].split('=')[1].split(';')[0]
								break



					if arg != None and (arg.startswith('"') or arg.startswith("'")):
						arg = arg[1:len(arg)-1]
					elif arg != None:
						arg = self.findStringValue(fileReader, u, arg)

		return arg

	def checkSetDataArg(self, fileReader, intentsWithSetData):
		In = []
		NotIn = []

		for intent in intentsWithSetData:
			instr = intent[R.INSTR].strip()
			
			if 'Uri.parse(' in instr:
				arg = instr.split('Uri.parse(')[1].split(')')[0]

				if arg.startswith('"') or arg.startswith("'"):
					arg = arg[1:len(arg)-1]

				else:
					arg = self.findStringValue(fileReader, intent, arg)
			else:
				#if 'setData(' in instr:
				arg = instr.split('setData(')[1].split(')')[0]
				arg = self.findUriValue(fileReader, intent, arg)
				#else:
				#	arg = None

			if arg != None and arg.startswith('content'):
				In.append(intent)

			elif arg != None and arg.startswith('file'):
				NotIn.append(intent)

		return In, NotIn

	def checkAddFlagsArg(self, intents, intentsWithAddFlags):
		In = []
		NotIn = []

		for intent in intents:
			isIn = False

			for iFlag in intentsWithAddFlags:

				if intent[R.VALUE] == iFlag[R.VALUE]:
					if ((intent[R.SCOPE] == R.VARGLOBAL and iFlag[R.SCOPE] == intent[R.SCOPE]) or 
						(intent[R.SCOPE] == R.VARCLASS and iFlag[R.SCOPE] == intent[R.SCOPE] and iFlag[R.CLASSID] == intent[R.CLASSID]) or
						(intent[R.SCOPE] == R.VARLOCAL and iFlag[R.SCOPE] == intent[R.SCOPE] and intent[R.CLASSID] == iFlag[R.CLASSID] and intent[R.FUNCID] == iFlag[R.FUNCID])):
						isIn = True
						arg = iFlag[R.INSTR].split('addFlags(')[1].split(')')[0]

						if ("FLAG_GRANT_READ_URI_PERMISSION" in arg) or ("FLAG_GRANT_WRITE_URI_PERMISSION" in arg):
							In.append(intent)
						else:
							NotIn.append(intent)
						break


			if isIn == False:
				NotIn.append(intent)

		return In, NotIn


	def run(self):
		self.loading()

		for f in self.javaFiles:
			fileReader = FileReader(f)

			found = Parser.finder(fileReader,
									[[Parser.findVarName, (['Intent '], None)],
									 [Parser.findObjName, ('setData', None)],
									 [Parser.findObjName, ('addFlags', None)]])


			# Get all intents names
			intents = found[0]
			# Get all intents which use 'setData' method
			intentsWithSetData = found[1]
			# Get all intents which use 'addFlags' method
			intentsWithAddFlags = found[2]

			intents = Parser.setScopes(intents)
			intentsWithSetData = Parser.setScopesWith(intentsWithSetData, intents)
			intentsWithAddFlags = Parser.setScopesWith(intentsWithAddFlags, intents)

			# Check arg given to 'setData'
			In, NotIn = self.checkSetDataArg(fileReader, intentsWithSetData)

			# Set log msg
			NotIn = Parser.setMsg(NotIn, R.CRITICAL, self.errMsg1)

			# Check arg given to 'addFlags'
			In, NotIn2 = self.checkAddFlagsArg(In, intentsWithAddFlags)

			# Set log msg
			NotIn2 = Parser.setMsg(NotIn2, R.CRITICAL, self.errMsg2)

			NotIn = NotIn + NotIn2

			self.updateOCN(f, In, NotIn, (len(NotIn)  == 0 and len(In) == 0))
			self.loading()
			fileReader.close()

		self.store(9, self.AndroidOkMsg, self.AndroidErrMsg, self.AndroidText, self.category, False, [self.errMsg2])
		self.display(FileReader)


