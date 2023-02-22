#!/usr/bin/python3

from Rules import *
from XmlReader import *
from Parser import *
from R import *
from Common import *
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


	def run(self):
		self.loading()

		if self.manifest != None:
			xmlReader = XmlReader(self.manifest)

			providersArgs = Common.get_xml_tag_args(xmlReader, "provider")
			permissionsArgs = Common.get_xml_tag_args(xmlReader, "permission")
			sdkArgs = Common.get_xml_tag_args(xmlReader, "uses-sdk")

			isOldSdk = False
			if len(sdkArgs) == 0:
				isOldSdk = True
			else:
				args = sdkArgs[0][XmlReader.ARGS]
				argIndex, argValue = Common.get_arg_index_and_value(args, 'android:minSdkVersion=')
				# print(f'{argValue}  ')
				if argIndex >= 0:
					version = int(argValue)
					if version <= 16:
						isOldSdk = True

			########################################
			#  check if the provider is exported   #
			########################################
			pIsExported		= []
			pIsNotExported 	= []
			# for each content provider, check 'android:exported'
			for p in providersArgs:
				args = p[XmlReader.ARGS]
				exportedIndex, exportedValue = Common.get_arg_index_and_value(args, 'android:exported=') # greatest degree of generalization
				if exportedIndex >= 0:			# android:exported argument is present
					if exportedValue == 'true':
						pIsExported.append(p)
					else:
						pIsNotExported.append(p)
				else:							# android:exported argument is not present
					if isOldSdk:
						pIsExported.append(p)
					else:
						pIsNotExported.append(p)

			########################################
			#     Check for custom permission      #
			########################################
			listSignatures = []
			# Get all signature names
			for permission in permissionsArgs:
				args = permission[XmlReader.ARGS]
				protectionLevelIndex, protectionLevelValue = Common.get_arg_index_and_value(args, 'android:protectionLevel=')
				if protectionLevelIndex >= 0:
					if protectionLevelValue == "signature":
						nameIndex, nameValue = Common.get_arg_index_and_value(args, 'android:name=')
						if nameIndex >= 0:
							listSignatures.append(nameValue)

			# Check for all pIsExported if a permission found is used
			pIsSecure = []
			for exportedProvider in pIsExported:
				args = exportedProvider[XmlReader.ARGS]
				permIndex, permValue = Common.get_arg_index_and_value(args, 'android:permission=')
				readPermIndex, readPermValue = Common.get_arg_index_and_value(args, 'android:readPermission=')
				writePermIndex, writePermValue = Common.get_arg_index_and_value(args, 'android:writePermission=')			

				permissionName = ""
				if permIndex >= 0:
					permissionName = permValue
				elif readPermIndex >= 0:
					permissionName = readPermValue
				elif writePermIndex >= 0:
					permissionName = writePermValue

				if permissionName != "" and permissionName in listSignatures:
					pIsSecure.append(exportedProvider)

			pIsExported = [x for x in pIsExported if x not in pIsSecure]

			# # format data to be display in 'Display' class
			In = xmlReader.constructToken(pIsNotExported + pIsSecure)

			# # Set log msg
			In 		= Parser.setMsg(In, R.OK)
			NotIn = Common.set_err_msg(pIsExported, self.errMsg)

			self.just_update(xmlReader.getFile(), NotIn)

			xmlReader.close()
			self.loading()

			self.store(2, self.AndroidOkMsg, self.AndroidErrMsg, self.AndroidText, self.category)
			self.display(XmlReader)
		else:
			self.loading()