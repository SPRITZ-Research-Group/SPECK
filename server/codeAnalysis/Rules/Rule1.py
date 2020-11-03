#!/usr/bin/python3

from Rules import *
from FileReader import *
from Parser import *
from R import *
import sys


'''
RULE N°1

+ Show an App Chooser
** Show an app chooser when an implicit intent can launch at least two possible apps
-> https://developer.android.com/topic/security/best-practices#intent-content-provider

? Pseudo Code:
	1. Get all implicit intents (with ACTION_SEND and ACTION_GET_CONTENT)
	2. Get all intents which use 'createChooser'
	3. Compare

! Output
	-> NOTHING	: no implicit intent found
	-> OK 	   	: implicit intent which respect the rule
	-> CRITICAL	: implicit intent which doesn't respect the rule
'''

class Rule1(Rules):
	def __init__(self, directory, database, verbose=True, verboseDeveloper=False, storeManager=None, flowdroid=False, platform="", validation=False, quiet=True):
		Rules.__init__(self, directory, database, verbose, verboseDeveloper, storeManager, flowdroid, platform, validation, quiet)	
		
		self.AndroidErrMsg = "implicit intent(s) (don't) use an app chooser"
		self.AndroidOkMsg = "implicit intent(s) use() an app chooser"
		self.AndroidText = "https://developer.android.com/topic/security/best-practices#intent-content-provider"

		self.okMsg = "Show an app chooser when an implicit intent can launch at least two possible apps"
		self.errMsg = "'Intent.createChooser' is not called for an implicit intent which use ACTION_SEND/ACTION_GET_CONTENT"
		self.category = R.CAT_1

		self.filter('android.content.Intent')
		self.show(1, "Show an App Chooser")

	def checkArg(self, createChooserIntents, intentActions):
		In = []

		for e in createChooserIntents:
			instr = e[R.INSTR]
			instr = instr.split("Intent.createChooser")[1].strip()
			instr = instr.split(",")[0].strip()

			if 'new Intent' in instr:
				if 'setAction(' in instr:
					instr = instr.split('setAction(')[1].split(")")[0].strip()
				else:
					instr = instr.split("new Intent")[1].split("(")[1].split(")")[0].strip()

				if any(elem in instr for elem in intentActions):
					In.append(e)

		return In

	def getSetAction(self, intents, setAction):
		whiteList = ['ACTION_SEND', 'ACTION_GET_CONTENT', '"android.intent.action.SEND"', '"android.intent.action.GET_CONTENT"']

		res = []
		for elem in setAction:
			if any(e in elem[R.INSTR] for e in whiteList):
				res.append(elem)

		setAction = Parser.setScopesWith(res, intents)

		res = []
		for e in setAction:
			if e[R.SCOPE] != None:
				res.append(e)

		return res


	def run(self):
		self.loading()
		for f in self.javaFiles:
			fileReader = FileReader(f)

			found = Parser.finder(fileReader,
									[[Parser.findVarName, (['Intent '], None)],
									 [Parser.findVarName, (['Intent', 'new', 'ACTION_SEND'], None)],
									 [Parser.findVarName, (['Intent', 'new', 'ACTION_GET_CONTENT'], None)],
									 [Parser.findVarName, (['Intent', 'new', '"android.intent.action.SEND"'], None)],
									 [Parser.findVarName, (['Intent', 'new', '"android.intent.action.GET_CONTENT"'], None)],
									 [Parser.findArgName, ('Intent.createChooser', 0, None)],
									 [Parser.findObjName, ('setAction', None)]])

			# Get all intents names
			intents = found[0]
			# Get all implicit intents names
			implicitIntents = found[1] + found[2] + found[3] + found[4]
			# Get all intents used in a 'createChooser' function
			createChooserIntents = found[5]
			# Get intents which use 'setAction' method
			setAction = found[6]

			# Set scope of all intents declared
			intents = Parser.setScopes(intents)
			# Set scope for all implicit intents
			implicitIntents = Parser.setScopesWith(implicitIntents, intents)
			# diff between implicitIntents and createChooserIntents
			In, NotIn = Parser.diff(implicitIntents + self.getSetAction(intents, setAction), createChooserIntents)
			# Case where Intent is instantiate in Intent.createChooser parameter
			In2 = self.checkArg(createChooserIntents, ['ACTION_SEND', 'ACTION_GET_CONTENT', '"android.intent.action.SEND"', '"android.intent.action.GET_CONTENT"'])
			In = In + In2

			# Set log msg
			In 		= Parser.setMsg(In, R.OK)
			NotIn 	= Parser.setMsg(NotIn, R.CRITICAL, self.errMsg)

			self.updateOCN(f, In, NotIn, (len(implicitIntents) == 0 and len(In) == 0))
			self.loading()
			fileReader.close()

		self.store(1, self.AndroidOkMsg, self.AndroidErrMsg, self.AndroidText, self.category, False, [self.errMsg])

		self.display(FileReader)
