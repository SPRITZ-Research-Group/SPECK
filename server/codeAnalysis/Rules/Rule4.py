#!/usr/bin/python3

from Rules import *
from XmlReader import *
from Parser import *
from R import *
import sys


'''
RULE N°4

+ Use intents to defer permissions
** Whenever possible, don't add a permission to your app to complete an action that could be completed in another app.
** Instead, use an intent to defer the request to a different app that already has the necessary permission.
-> https://developer.android.com/topic/security/best-practices#permissions
-> https://developer.android.com/guide/topics/permissions/overview#permission-groups

? Pseudo Code:
	1. Get all permissions' names
	2. Compare with a blacklist

! Output
	-> NOTHING	: no dangerous permission found
	-> WARNING	: dangerous permission found
'''

class Rule4(Rules):
	def __init__(self, directory, database, verbose=True, verboseDeveloper=False, storeManager=None, flowdroid=False, platform="",validation=False, quiet=True):
		Rules.__init__(self, directory, database, verbose, verboseDeveloper, storeManager, flowdroid, platform, validation, quiet)

		self.AndroidErrMsg = "permission(s) complete actions that could be completed by another app"
		self.AndroidOkMsg = "no dangerous permission is used"
		self.AndroidText = "https://developer.android.com/topic/security/best-practices#permissions"

		self.okMsg = "There is no permission to defer"		
		self.errMsg = "There are permissions whose action can be completed by another system app"
		self.category = R.CAT_1
		
		self.findXml()
		self.show(4, "Use intents to defer permissions")

	def getDangerousPermissions(self, xmlReader, permissions):
		prefix = "android.permission."
		
		blackList = ['READ_CALENDAR'	, 'WRITE_CALENDAR'			, 'CAMERA', 'READ_CONTACTS'	, 'WRITE_CONTACTS'	,
					 'GET_ACCOUNTS'		, 'ACCESS_FINE_LOCATION'	, 'ACCESS_COARSE_LOCATION'	, 'RECORD_AUDIO'	,
					 'READ_PHONE_NUMBERS'		, 'READ_SMS'				, 'RECEIVE_SMS'		,
					 'CALL_PHONE'		, 'ANSWER_PHONE_CALLS'		, 'READ_CALL_LOG'			, 'WRITE_CALL_LOG'	,
					 'USE_SIP'			, 'PROCESS_OUTGOING_CALLS', 'SEND_SMS'		, 
					 'RECEIVE_WAP_PUSH'	, 'RECEIVE_MMS'				, 'READ_EXTERNAL_STORAGE'	, 'ADD_VOICEMAIL' ]
		'''
		-> What to use to avoid these dangerous permissions ?
		CALENDAR 	: CalendarContract
		CAMERA	 	: MediaStore
		CONTACTS 	: ContactsContract
		LOCATION 	: Intent.ACTION_VIEW
		MICROPHONE 	: MediaRecorder
		PHONE 		: Intent.ACTION_DIAL
		SENSORS 	: SensorManager
		SMS 		: Intent.ACTION_SEND
		STORAGE 	: Intent.ACTION_GET_CONTENT
		'''
		blackList = [prefix + s for s in blackList]

		dangerousPermissions = []
		for p in permissions:
			for arg in p[XmlReader.ARGS]:
				if 'android:name=' in arg:
					value = xmlReader.getArgValue(arg)
					if value in blackList:
						dangerousPermissions.append(p)
					break

		return dangerousPermissions


	def run(self):
		self.loading()
		if self.manifest != None:
			xmlReader = XmlReader(self.manifest)

			permissions = xmlReader.getArgsTag("uses-permission")

			dangerousPermissions = self.getDangerousPermissions(xmlReader, permissions)

			# format data to be display in 'Display' class
			NotIn = xmlReader.constructToken(dangerousPermissions)
			# Set log msg
			NotIn 	= Parser.setMsg(NotIn, R.WARNING, self.errMsg)

			self.updateWN(xmlReader.getFile(), NotIn)

			self.loading()
			xmlReader.close()

			self.store(4, self.AndroidOkMsg, self.AndroidErrMsg, self.AndroidText, self.category, True)
			self.display(XmlReader)

		else:
			self.loading()


