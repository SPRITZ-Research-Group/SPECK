#!/usr/bin/python3

from Rules import *
from FileReader import *
from Parser import *
from R import *
import sys
from Common import *


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
	def __init__(self, directory, database, verbose=True, verboseDeveloper=False, storeManager=None, flowdroid=False, platform="",validation=False, quiet=True):
		Rules.__init__(self, directory, database, verbose, verboseDeveloper, storeManager, flowdroid, platform, validation, quiet)
		
		self.AndroidErrMsg = "implicit intent(s) (don't) use an app chooser"
		self.AndroidOkMsg = "implicit intent(s) use() an app chooser"
		self.AndroidText = "https://developer.android.com/topic/security/best-practices#intent-content-provider"

		self.okMsg = "Show an app chooser when an implicit intent can launch at least two possible apps"
		self.errMsg = "'Intent.createChooser' is not called for an implicit intent which use ACTION_SEND/ACTION_GET_CONTENT"
		self.category = R.CAT_1

		self.filter('android.content.Intent')

		self.show(1, "Show an App Chooser")


	def run(self):
		self.loading()

		intentActions = ['ACTION_SEND', 'ACTION_GET_CONTENT', '"android.intent.action.SEND"', '"android.intent.action.GET_CONTENT"']

		for f in self.javaFiles:
			fileReader = FileReader(f)

			# Get all intents names
			intents = Common.get_all_var_names(fileReader, ['Intent '])

			# Get all implicit intents names
			implicitIntents = Common.get_all_var_names(fileReader, ['Intent', 'new', 'ACTION_SEND'])
			implicitIntents += Common.get_all_var_names(fileReader, ['Intent', 'new', 'ACTION_GET_CONTENT'])
			implicitIntents += Common.get_all_var_names(fileReader, ['Intent', 'new', '"android.intent.action.SEND"'])
			implicitIntents += Common.get_all_var_names(fileReader, ['Intent', 'new', '"android.intent.action.GET_CONTENT"'])

			# Get all intents used in a 'createChooser' function
			createChooserIntents = Common.get_all_arg_names(fileReader, 'Intent.createChooser', 0)
			
			# Get intents which use 'setAction' method
			setAction = Common.get_all_obj_names(fileReader, 'setAction')

			# compare implicitIntents and createChooserIntents
			compImpliciIntents = implicitIntents + Common.match_obj_with_vars(intents, setAction, intentActions)
			In, NotIn = Common.compare(compImpliciIntents, createChooserIntents, with1=True, scope_with1=intents)

			# Set log msg
			NotIn 	= Parser.setMsg(NotIn, R.CRITICAL, self.errMsg) # Almost standard

			if len(NotIn) > 0:

				
				uriSetters = Common.get_all_obj_names(fileReader, 'setData')
				uriSetters += Common.get_all_obj_names(fileReader, 'setDataAndNormalize')
				uriSetters += Common.get_all_obj_names(fileReader, 'setDataAndType')
				uriSetters += Common.get_all_obj_names(fileReader, 'setDataAndTypeAndNormalize')

				if len(uriSetters) > 0:
					test = Common.get_all_var_types(fileReader, 'activity,')

				NotIn += uriSetters
			########################################
			#     What we need for the attack      #
			########################################
			# - intent action
			# - uri

			# Almost standard
			self.updateOCN(f, In, NotIn, (len(implicitIntents) == 0 and len(In) == 0))
			self.loading()
			fileReader.close()

		self.store(1, self.AndroidOkMsg, self.AndroidErrMsg, self.AndroidText, self.category, False, [self.errMsg])

		self.display(FileReader)

