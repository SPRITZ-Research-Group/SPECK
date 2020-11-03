#!/usr/bin/python3

from Rules import *
from XmlReader import *
from FileReader import *
from Parser import *
from R import *
import sys


'''
RULE N°3

+ Provide the right permissions
** app should request only the minimum number of permissions necessary to function properly
-> https://developer.android.com/topic/security/best-practices#permissions
-> https://github.com/reddr/axplorer/tree/master/permissions

? Pseudo Code:
	1. Get all permissions' names in <uses-permission> tag
	2. Get targetSdkVersion
	3. From framework/sdk map files, extract functions' names for each permission found
	4. From cp map files, extract URI names for each permission found
	5. Check these names/URIs in all java files

! Output
	-> NOTHING	: no permission not used found
	-> CRITICAL	: permission not used found
'''

class Rule3(Rules):
	def __init__(self, directory, database, verbose=True, verboseDeveloper=False, storeManager=None, flowdroid=False, platform="",validation=False, quiet=True):
		Rules.__init__(self, directory, database, verbose, verboseDeveloper, storeManager, flowdroid, platform, validation, quiet)

		self.mapDir = './codeAnalysis/permissions-mapping/'

		self.AndroidErrMsg = "permission(s) (are) useless"
		self.AndroidOkMsg = "no permission used is useless"
		self.AndroidText = "https://developer.android.com/topic/security/best-practices#permissions"

		self.okMsg = "There is no permission useless"
		self.errMsg = "The app should request only the minimum number of permissions"
		self.category = R.CAT_3
		
		self.findXml()
		self.show(3, "Provide the right permissions")

	def getPermissions(self, xmlReader, permissionsArgs):
		perm = []
		for p in permissionsArgs:
			for arg in p[XmlReader.ARGS]:
				if 'android:name=' in arg:
					value = xmlReader.getArgValue(arg)
					perm.append(value)
					break
		return perm

	def getFuncMapped(self, permissions, sp):
		functions = []

		# SDK-MAP AND FRAMEWORK-MAP FILES
		mapFiles = [self.mapDir + 'sdk-map-'+ self.targetSdkVersion + '.txt', self.mapDir + 'framework-map-'+ self.targetSdkVersion + '.txt']
		for mapFile in mapFiles:
			with open(mapFile) as file:
				while True:
					line = file.readline()
					if line == '':
						break

					p = line.split(sp)[1].strip().split(', ')
					index = 0
					for elem in p:
						if elem.strip() in permissions:
							index += 1

					if index != 0: 
						functions.append([line.split(sp)[0].strip(), line.split(sp)[1].strip()])

		return functions

	def getCpMapped(self, permissions):
		contents = []

		# CP-MAP FILE
		with open(self.mapDir + 'cp-map-'+ self.targetSdkVersion + '.txt') as file:
			while True:
				line = file.readline()
				if line == '':
					break
				
				if "[grant-uri-permission]" not in line:
					p = ' '.join(line.split()).split(' ')[-1]

					if p in permissions:
						# [package name, content, permission]
						contents.append([' '.join(line.split()).split(' ')[0], ' '.join(line.split()).split(' ')[1], p])

		return contents

	def extractPkgNames(self, package):
		pkgList = []

		split = package.split('.')
		pkg = split[0]+".*"
		for i in range(1, len(split)-1):
			pkgList.append(pkg)
			pkg = pkg[0:len(pkg)-2]+"."+split[i]+".*"
		
		pkgList.append(pkg[0:len(pkg)-2]+".*")
		pkgList.append(pkg[0:len(pkg)-2])
		pkgList.append(package)

		return pkgList

	def packageIsIn(self, packageList, packagesImported):
		for listElem in packageList:
			for pImported in packagesImported:
				if listElem == pImported:
					return True

		return False

	def getAllPkg(self, funcNames, contentNames):
		pkgs = []

		for e in funcNames:
			pkgs += self.extractPkgNames(e[0].split('(')[0])
		for e in contentNames:
			pkgs += self.extractPkgNames(e[0])
		
		return pkgs

	def getNotCalled(self, funcNames, contentNames):
		cpy = funcNames.copy()
		cpyContent = contentNames.copy()

		filt = Filter(self.directory, self.getAllPkg(funcNames, contentNames))
		javaFiles = filt.execute() 

		self.maxFiles = len(javaFiles)

		for file in javaFiles:
			self.loading()
			packagesImported = []

			fileReader = FileReader(file)
			line, tok = fileReader.getNextInstruction()
			while line != '':
				# Get all packages in file
				if 'import ' in line:
					packagesImported.append(line.split(' ')[1].split(';')[0].strip())
				else:

					''' FUNCNAMES '''
					for elem in cpy:
						funcName = elem[0].split('(')[0].split('.')[-1]
						package = elem[0].split('(')[0]

						# Get all packages extension
						packageList = self.extractPkgNames(package)

						# Check if function and package are in the file
						if (((funcName+'(' or funcName+' (') in line) 
							and self.packageIsIn(packageList, packagesImported)):
							funcNames.remove(elem)

							# remove also other functions with the same permission
							listPerm = elem[-1].split(', ')
							for f in cpy:
								for perm in listPerm:
									if perm in f[-1]:
										try:
											funcNames.remove(f)
										except:
											pass

					cpy = funcNames

					''' CONTENTNAMES '''
					for elem in cpyContent:
						cName = elem[1]
						package = elem[0]

						# Get all packages extension
						packageList = self.extractPkgNames(package)

						# Check if content and package are in the file
						if ((cName in line) 
							and self.packageIsIn(packageList, packagesImported)):
							contentNames.remove(elem)

							# remove also other functions with the same permission
							for f in cpyContent:
								if elem[-1] == f[-1]:
									try:
										contentNames.remove(f)
									except:
										pass

					cpyContent = contentNames

				line, tok = fileReader.getNextInstruction()

			fileReader.close()
			
		permissions = []
		for e in funcNames:
			permissions.append(e[-1])
		for e in contentNames:
			permissions.append(e[-1])

		return permissions

	def getPermissionsNotUsed(self, xmlReader, permissionsArgs, notUsed):
		permNotUsed = []

		for p in permissionsArgs:
			for arg in p[XmlReader.ARGS]:
				if 'android:name=' in arg:
					value = xmlReader.getArgValue(arg)

					for elem in notUsed:
						if value in elem.split(', '):
							permNotUsed.append(p)
							break
					break

		return permNotUsed

	def getTargetSdkVersion(self, xmlReader):
		tag = xmlReader.getArgsTag("uses-sdk")

		tagM = xmlReader.getArgsTag("manifest")

		for t in tag:
			for arg in t[XmlReader.ARGS]:
				if "android:targetSdkVersion=" in arg:
					value = xmlReader.getArgValue(arg)

					if os.path.isfile(self.mapDir + 'sdk-map-'+ value + '.txt'):
						self.targetSdkVersion = value
						return

		for t in tagM:
			for arg in t[XmlReader.ARGS]:
				if "platformBuildVersionCode=" in arg:
					value = xmlReader.getArgValue(arg)

					if os.path.isfile(self.mapDir + 'sdk-map-'+ value + '.txt'):
						self.targetSdkVersion = value
						return

		self.targetSdkVersion = None

	def run(self):
		self.loading()

		if self.manifest != None:
			xmlReader = XmlReader(self.manifest)

			# 1. Get targetSdkVersion 
			self.getTargetSdkVersion(xmlReader)

			if self.targetSdkVersion != None:

				# 2. Get all permissions in Manifest File
				permissionsArgs = xmlReader.getArgsTag("uses-permission")
				permissions = self.getPermissions(xmlReader, permissionsArgs)
				
				# 3. Get all functions names associated with permissions found in FRAMEWORK/SDK files
				funcNames = self.getFuncMapped(permissions, '::')
				# 4. Get all contents  associated with permissions found in CP file
				contentNames = self.getCpMapped(permissions)

				# 5. Get all 'funcNames' / 'contentNames' not used in .java files
				notUsed = self.getNotCalled(funcNames, contentNames)

				permissionsNotUsed = self.getPermissionsNotUsed(xmlReader, permissionsArgs, notUsed)

				# format data to be display in 'Display' class
				NotIn = xmlReader.constructToken(permissionsNotUsed)
				# Set log msg
				NotIn = Parser.setMsg(NotIn, R.CRITICAL, self.errMsg)

				if len(NotIn) > 0:
					self.filter("")

				self.updateCN(xmlReader.getFile(), NotIn)

				xmlReader.close()
				self.loading()

				self.store(3, self.AndroidOkMsg, self.AndroidErrMsg, self.AndroidText, self.category, True)
				self.display(XmlReader)

			else:
				xmlReader.close()
				self.loading()
				self.updateN()

				self.store(3, self.AndroidOkMsg, self.AndroidErrMsg, self.AndroidText, self.category, True)
				self.display(XmlReader)

		else:
			self.loading()






