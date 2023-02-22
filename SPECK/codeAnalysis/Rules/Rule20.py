#!/usr/bin/python3

from Rules import *
from XmlReader import *
from FileReader import *
from Parser import *
from R import *
import sys


'''
RULE N°20

+ Use services
** if you add any intent filters to the service declaration, it is exported by default. It's best if you explicitly declare the android:exported attribute.
-> https://developer.android.com/training/articles/security-tips#Services

? Pseudo Code:
	1. Check for <intent-filter> inside <service> # TOBEFIXED --> just check if <service> has intent-filter or android:exported=true
	2. If yes, look for android:exported
	3. If the developer has used the android:permission attribute, then he should have also used checkCallingPermission()

! Output
	-> NOTHING	: no service found
	-> WARNING	: service which use an intent filter doesn't use 'exported' attribute
	-> OK 		: service which use an intent filter use 'exported' attribute
'''

class Rule20(Rules):
	def __init__(self, directory, database, verbose=True, verboseDeveloper=False, storeManager=None, flowdroid=False, platform="",validation=False, quiet=True):
		Rules.__init__(self, directory, database, verbose, verboseDeveloper, storeManager, flowdroid, platform, validation, quiet)

		self.AndroidErrMsg = "service(s) which can be invoked by other apps (don't) explicit it"
		self.AndroidOkMsg = "service(s) which can be invoked by other apps (are) well declared"
		self.AndroidText = "https://developer.android.com/training/articles/security-tips#Services"

		self.okMsg = "Service well implemented. Tou can also protect it using the android:permission attribute"
		self.errMsg = "Service has to explicitly use android:exported attribute"
		#self.errMsg2 = "If a service use android:permission attribute, checkCallingPermission() method has to be implemented"
		self.errMsg2 = "If a service is exported, it needs to either use the android:permission attribute, or call the checkCallingPermission() method"
		self.category = R.CAT_1
		
		self.findXml()
		self.show(20, "Use services")

	def with_intent_filter(tag):
		print(tag)
		return False

	# In: unexported services
	# NotIn: exported services, need to check for permissions
	def checkExportedWithoutFilter(self, services):
		In = []
		NotIn = []
		
		for s in services:
			isIn = True
			for arg in s[XmlReader.ARGS]:
				if 'android:exported="true"' in arg:
					isIn = False
					break
			if isIn:
				In.append(s)
			else:
				NotIn.append(s)
		return In, NotIn

	# In: exported explicitly, need to check permissions
	# NotIn: not exported explicitly
	def checkExported(self, services):
		In = []
		MaybeIn = []
		NotIn = []

		for s in services:
			added = False
			for arg in s[XmlReader.ARGS]:
				if 'android:exported="false"' in arg:
					In.append(s)
					added = True
					break
				if 'android:exported="true"' in arg:
					MaybeIn.append(s)
					added = True
					break
			if not added:
				NotIn.append(s)

		return In, MaybeIn, NotIn

	def searchPermissionChecking(self, serviceName):
		self.filter('android.app.Service')
		self.loading()

		for f in self.javaFiles:
			fileReader = FileReader(f)

			listClss, listFunc = Parser.getClassNFunc(fileReader)

			whitelist = ["checkCallingPermission(", "checkCallingPermission ("]
			for clss in listClss:
				if serviceName.split('.')[-1] in clss[R.INSTR]:
					isOk = False
					for func in listFunc:
						if func[R.CLASSID] == clss[R.CLASSID]:
							if any(elem in func[R.INSTR] for elem in whitelist):
								isOk = True
								break

					return isOk

			self.loading()
			fileReader.close()

		return False

	def checkPermission(self, xmlReader):
		In = []
		NotIn = []

		services = xmlReader.getArgsTag("service")

		for s in services:
			isIn = False
			name = ""
			for arg in s[XmlReader.ARGS]:
				if "android:permission" in arg:
					isIn = True
				if "android:name" in arg:
					name = xmlReader.getArgValue(arg)
			if isIn:
				if self.searchPermissionChecking(name):
					In.append(s)
				else:
					NotIn.append(s)

		return In, NotIn

	def checkPermissionV2(self, xmlReader, services):
		In = []
		NotIn = []

		for s in services:
			isIn = False
			name = ""
			for arg in s[XmlReader.ARGS]:
				if "android:permission" in arg:
					isIn = True
				if "android:name" in arg:
					name = xmlReader.getArgValue(arg)
			if isIn:
				In.append(s)
			elif self.searchPermissionChecking(name):
				In.append(s)
			else:
				NotIn.append(s)

		return In, NotIn


	def run(self):
		self.loading()

		if self.manifest != None:
			xmlReader = XmlReader(self.manifest)

			# get services which contain intent-filter 
			services_filter = xmlReader.getArgsCond("service", "intent-filter")
			# get services which do not contain intent-filter 
			services = xmlReader.getArgsNegCond("service", "intent-filter")
			In, MaybeIn, NotIn = self.checkExported(services_filter)
			In2, NotIn2 = self.checkExportedWithoutFilter(services)
			#In2, NotIn2 = self.checkPermission(xmlReader)
			In3, NotIn3 = self.checkPermissionV2(xmlReader, MaybeIn + NotIn2)

			# format data to be display in 'Display' class
			#In = xmlReader.constructToken(In+In2)
			#NotIn = xmlReader.constructToken(NotIn)
			#NotIn2 = xmlReader.constructToken(NotIn2)

			In = xmlReader.constructToken(In3 + In2 + In)
			NotIn = xmlReader.constructToken(NotIn)
			NotIn3 = xmlReader.constructToken(NotIn3)
			# set log message
			In = Parser.setMsg(In, R.OK)
			NotIn = Parser.setMsg(NotIn, R.WARNING, self.errMsg)
			NotIn3 = Parser.setMsg(NotIn3, R.WARNING, self.errMsg2)

			self.updateOWN(xmlReader.getFile(), In, NotIn+NotIn3, (len(In) == 0 and len(In) == 0))

			xmlReader.close()
			self.loading()

			self.store(20, self.AndroidOkMsg, self.AndroidErrMsg, self.AndroidText, self.category)
			self.display(XmlReader)

		else:
			self.loading()
