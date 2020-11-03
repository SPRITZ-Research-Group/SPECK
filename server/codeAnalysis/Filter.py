#!/usr/bin/python3

from Parser import *
from Timer import *
import os

class Filter():
	def __init__(self, directory, packages):
		self.directory = directory
		self.packages = packages

	def getPackagesImported(self, f):
		packagesImported = []
		while True:
			line = f.readline()
			if (line == ''):
				break
			line = ' '.join(line.split()).strip()
			if line.startswith('import'):
				line = line.split(' ')[1]
				package = line.split(';')[0]
				packagesImported.append(package)
			elif (line != '') and (not line.startswith('package')) and ('//' not in line) and ('/*' not in line):
				break
		return packagesImported

	def execute(self):
		files = []

		javaFiles = Parser.getAllPath(self.directory, '.java')

		os.system("rm test_imports.txt")

		for file in javaFiles:
			with open(file, 'r') as f:
				packagesImported = self.getPackagesImported(f)

				myfile = open("test_imports.txt", "a")

				for p in packagesImported:
					myfile.write(f'{p}\n')

				myfile.close()

				if self.packages[0] == "":
					break

				# Add file to the list IF ONE package was found
				for p in self.packages:
					if p in packagesImported:
						files.append(file)
						break
		return files
