#!/usr/bin/python3

from Parser import *
from Timer import *


class Filter():

	def __init__(self, directory, packages):
		self.directory = directory
		self.packages = packages


	# this function gets all the packages imported in the java file f
	def getPackagesImported(self, f):
		packagesImported = []
		while True:
			line = f.readline()
			if line == '':
				break
			line = ' '.join(line.split()).strip()
			if line.startswith('import'):
				line = line.split(' ')[1]
				package = line.split(';')[0]
				# print(f'{f.name}: {package}')
				packagesImported.append(package)
			elif (line != '') and (not line.startswith('package')) and ('//' not in line) and ('/*' not in line):
				break
		return packagesImported


	# returns all the files which import the "interesting" packages
	# ONE imported package is enough to keep the file
	def execute(self):
		files = []
		javaFiles = Parser.getAllPath(self.directory, '.java')
		for n,file in enumerate(javaFiles):
			with open(file, 'r') as f:
				packagesImported = self.getPackagesImported(f)
				# print(packagesImported)
				# Add file to the list IF ONE package was found
				for p in self.packages:
					if p == "":					# kind of a 'naive' default: analyze all .java files
						files.append(file)
						break	
					if p in packagesImported:
						files.append(file)
						break
		return files

