#!/usr/bin/python3

from Rules import *
from XmlReader import *
from Parser import *
from R import *
import sys


'''
RULE N°2

+ Control Access to yours Content Providers
** Apply signature-based permissions if you want to share data between 2 apps you own
** Disallow access to your app's content providers if you don't want to share data
-> https://developer.android.com/topic/security/best-practices#intent-content-provider
-> https://developer.android.com/guide/topics/manifest/provider-element#exported
-> https://www.codementor.io/maker-abhi/share-data-between-your-android-apps-only-securely-a0pa8ea0j

? Pseudo Code:
	1. Get all <provider>
	2. Check if they use a custom permission declared in a <permission>
	3. Otherwise, check if android:exported="false" is set (ONLY on API level 16 or lower)

! Output
	-> NOTHING	: no content provider found
	-> OK 	   	: content provider is enough restricted
	-> WARNING	: content provider can be more restricted
'''

class Rule2(Rules):
	def __init__(self, directory, database, verbose=True, verboseDeveloper=False, storeManager=None, flowdroid=False, platform="",validation=False, quiet=True):
		Rules.__init__(self, directory, database, verbose, verboseDeveloper, storeManager, flowdroid, platform, validation, quiet)

		self.AndroidErrMsg = "content provider(s) can still (have) an access more restricted"
		self.AndroidOkMsg = "content provider(s) (have) an access enough restricted"
		self.AndroidText = "https://developer.android.com/topic/security/best-practices#intent-content-provider"

		self.okMsg = "Some content providers have an access enough restricted"
		self.errMsg = "Restrict access to your content provider if you don't want share data with unknown apps"
		self.category = R.CAT_1

		self.findXml()
		self.show(2, "Control Access to Content Providers")


	def isLowerThan(self, xmlReader, sdk, nb):
		for s in sdk:
			if 'android:minSdkVersion' in s:
				version = int(xmlReader.getArgValue(s))
				if version <= nb:
					return True
		return False

	def accessDisallowed(self, providersArgs, isOldSdk):
		pIsExported		= []
		pIsNotExported 	= []

		# for each content provider, check 'android:exported'
		for p in providersArgs:
			if isOldSdk:
				isIn = False
				for arg in p[XmlReader.ARGS]:

					if 'android:exported="false"' in arg:
						pIsNotExported.append(p)
						isIn = True
						break
				if not isIn:
					pIsExported.append(p)
					
		return pIsExported, pIsNotExported

	def signatureBased(self, xmlReader, providersArgs, pIsExported, permissionsArgs):
		listSignatures = []
		# Get all signature names
		for permission in permissionsArgs:
			isSigned = False
			name = ""
			for arg in permission[XmlReader.ARGS]:
				if 'android:protectionLevel="signature"' in arg:
					isSigned = True
				if 'android:name=' in arg:
					name = xmlReader.getArgValue(arg)

			if isSigned:
				listSignatures.append(name)

		# Check for all pIsExported if a permission found is used
		pIsSecure = []
		check = 1
		for elem in pIsExported:
			for arg in elem[XmlReader.ARGS]:
				if ('android:permission=' in arg
					or 'android:readPermission=' in arg
					or 'android:writePermission=' in arg):
					permissionName = xmlReader.getArgValue(arg)

					if ((permissionName in listSignatures) and (('android:permission=' in arg)
						or ('android:readPermission=' in arg and check == 0)
						or ('android:writePermission=' in arg and check == 0))):
						pIsSecure.append(elem)
						break
					check -= 1

		pIsExported = [x for x in pIsExported if x not in pIsSecure]

		return pIsExported, pIsSecure


	def run(self):
		self.loading()

		if self.manifest != None:
			xmlReader = XmlReader(self.manifest)

			providersArgs 	= xmlReader.getArgsTag("provider")
			permissionsArgs = xmlReader.getArgsTag("permission")
			sdkArgs			= xmlReader.getArgsTag("uses-sdk")

			if len(sdkArgs) == 0:
				isOldSdk = True
			else:
				isOldSdk = self.isLowerThan(xmlReader, sdkArgs[0][XmlReader.ARGS], 16)
	
			pIsExported, pIsNotExported = self.accessDisallowed(providersArgs, isOldSdk)
			pIsExported, pIsSecure = self.signatureBased(xmlReader, providersArgs, pIsExported, permissionsArgs)

			# format data to be display in 'Display' class
			In = xmlReader.constructToken(pIsNotExported + pIsSecure)
			NotIn = xmlReader.constructToken(pIsExported)

			# Set log msg
			In 		= Parser.setMsg(In, R.OK)
			NotIn 	= Parser.setMsg(NotIn, R.WARNING, self.errMsg)

			self.updateOWN(xmlReader.getFile(), In, NotIn, (len(providersArgs) == 0))

			xmlReader.close()
			self.loading()

			self.store(2, self.AndroidOkMsg, self.AndroidErrMsg, self.AndroidText, self.category)
			self.display(XmlReader)
		else:
			self.loading()