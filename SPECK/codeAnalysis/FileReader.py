#!/usr/bin/python3

import tempfile
from Parser import *
from R import *
from Timer import *


class FileReader():
	def __init__(self, filename, toParse=True):
		self.filename 		= filename
		self.rootID 		= 0
		self.blockID 		= 0
		self.oBrace 		= 0
		self.cBrace 		= 0
		self.hasChanged 	= False
		self.inCommentary 	= False
		self.inTry 			= False
		self.classID 		= [[0, 0, False]]   # [ [ classID, blockID, inInterface ], ... ]
		self.clssId 		= 1
		self.funcID 		= [[0, 0]] 			# [ [ funcID, blockID ],  ... ]
		self.fID 			= 1
		self.className 		= [None]
		self.funcName 		= [None]
		self.package 		= ""
		self.nbOBraces 		= 0
		self.nbCBraces		= 0
		self.isInstr		= False
		self.tmp = tempfile.NamedTemporaryFile(mode='w+', delete=True)
		if toParse:
			self.parse()


	def parse(self):
		code = ""
		with open(self.filename, 'r') as f:
			while True:
				line = f.readline()
				if self.package == "":
					if "package" in line:
						self.package = line.split(" ")[1].replace(";", "")
				if line == '':
					break
				code += line
		code = FileReader.removeComments(code)
		code = FileReader.clearString(code)
		self.tmp.write(code)	# write data in temporary file
		self.tmp.seek(0)


	@staticmethod
	def removeComments(string):
		pattern = r"(\".*?(?<!\\)\"|\'.*?(?<!\\)\')|(/\*.*?\*/|//[^\r\n]*$)"
		# first group captures quoted strings (double or single)
		# second group captures comments (//single-line or /* multi-line */)
		regex = re.compile(pattern, re.MULTILINE|re.DOTALL)
		def _replacer(match):
			# if the 2nd group (capturing comments) is not None,
			# it means we have captured a non-quoted (real) comment string.
			if match.group(2) is not None:
				return "" # so we will return empty to remove the comment
			else: # otherwise, we will return the 1st group
				return match.group(1) # captured quoted-string
		return regex.sub(_replacer, string)


	# It removes useless space lines and Javadoc comment lines and puts '{' or '}' in newlines
	@staticmethod
	def clearString(code):
		output = []
		code_list = code.split('\n')			# get a list of the code by splitting according newlines
		code_list = [line for line in code_list if line != ' ' * len(line)]		# remove all space lines from 'code_list'
		check = False				# 'check' is needed to avoid to remove useful '*' lines, e.g. multiplication
		for line in code_list:			# if in a codeline we have '/*', '*/' or '*', then append a space line
			if '{"' in line and '"}' in line:
				output.append(line)
			elif '{' in line:
				line = line.replace("{", "\n{\n")
				output.append(line)
			elif '}' in line:
				line.replace("}", "\n}\n")
				output.append(line)
			else:
				output.append(line)
		output = [line for line in output if line != ' ' * len(line)]		# remove all space lines from 'output'
		return '\n'.join(output)				# return the string of the code after converting from list


	@staticmethod
	def clearLine(line):
		line = line.split('"')
		for i in range(0, len(line)):
			if i%2 != 0:
				line[i] = line[i].replace(";", "").replace("{", "").replace("}", "").replace("/*", '').replace("*/", '').replace("//", "")
			else:
				o = line[i].find("//")
				c = line[i].find("\n", o+1)
				if(o != -1 and c != -1):
					line[i] = line[i].replace(line[i][o:c+1], '')
		return '"'.join(line)
	

	def constructToken(self, line):
		return R.constructToken(self.rootID, self.blockID, self.classID[-1][0], self.funcID[-1][0], self.nbOBraces, self.nbCBraces, self.inTry, line, self.className, self.funcName, self.package)


	# It updates 'blockID' and 'rootID'
	def updateID(self, line):
		for c in line:
			if c == '{':
				self.nbOBraces += 1
				self.oBrace += 1
				self.hasChanged = True
			elif c == '}':
				self.nbCBraces += 1
				self.cBrace += 1
				self.hasChanged = True
			else:
				pass
			self.blockID = self.oBrace - self.cBrace
			if self.hasChanged and self.blockID == 0:
				self.rootID += 1
				self.oBrace = 0
				self.cBrace = 0
				self.hasChanged = False
		

	def getNextInstruction(self):
		self.isInstr = False
		line = self.tmp.readline()
		if line == '':
			token = self.constructToken(line)
			return line, token
		line = line.strip()

		self.updateID(line)		# update any info about 'line'

		if line.startswith('try'):		# Try / Catch
			self.inTry = True
		elif line.startswith('catch') or line.startswith('finally'):
			self.inTry = False

		elif line.startswith("/*"):		# Comment
			line = '\n'
			self.inCommentary = True
		elif line.startswith("*/"):
			line = '\n'
			self.inCommentary = False
		elif line.startswith("//"):
			line = '\n'
		elif self.inCommentary:
			line = '\n'

		elif line == '':		# Empty line
			line = '\n'

		elif line.startswith('default') or line.startswith('case') or line.startswith('switch'): 	# Switch
			pass

		elif line.startswith('@'):		# Special character
			line = '\n'
			pass

		elif line.startswith('if') or line.startswith('else'):		# If / Else
			self.isInstr = True
			pass

		elif line.startswith('for') or line.startswith('while'):	# For / While
			self.isInstr = True
			pass

		elif 'class ' in line and ';' not in line:		# Class
			self.classID.append([self.clssId, self.blockID+1, False])
			self.className.append(line.split("class ")[1].split(" ")[0].split("(")[0])
			self.clssId += 1
			pass

		elif 'interface ' in line and ';' not in line:		# Interface
			self.classID.append([self.clssId, self.blockID+1, True])
			self.className.append(line.split("interface ")[1].split(" ")[0].split("(")[0])
			self.clssId += 1
			pass

		elif line.startswith('{'):		# Block
			pass
		elif line.startswith('}'):
			if len(self.classID) > 1 and self.classID[-1][1] > self.blockID:
				del self.classID[-1]
				del self.className[-1]
			if len(self.funcID) > 1 and self.funcID[-1][1] > self.blockID:
				del self.funcID[-1]
				del self.funcName[-1]
			pass

		elif ';' not in line and '=' not in line and '(' in line and ')' in line:		# Function
			# and (line.startswith("public") or line.startswith("private") or line.startswith("protected"))
			self.funcID.append([self.fID, self.blockID+1])
			self.funcName.append(line.split("(")[0].split(" ")[-1])
			self.fID += 1
			pass

		else:						# Instruction & various
			self.isInstr = True
			pass

		token = self.constructToken(line)
		# print("token : ", token[R.PATH])
		# print("line  : ", line)
		# print("class : ", self.className)
		# print("func  : ", self.funcName)
		# print("pkg   : ", self.package)
		return line, token


	def close(self):
		self.tmp.close()
		self.tmp = None


	def resetCursor(self):
		if self.tmp != None:
			self.tmp.seek(0)
		self.rootID 		= 0
		self.blockID 		= 0
		self.oBrace 		= 0
		self.cBrace 		= 0
		self.hasChanged 	= False
		self.inCommentary 	= False
		self.inTry 			= False
		self.classID 		= [[0, 0, False]]
		self.clssId 		= 1
		self.funcID 		= [[0, 0]]
		self.fID 			= 1
		self.className 		= [None]
		self.funcName 		= [None]
		self.package 		= ""
		self.nbOBraces 		= 0
		self.nbCBraces		= 0
		self.isInstr		= False


	def getFilename(self):
		return self.filename


	def getClassID(self):
		return self.classID[-1][0]


	def isInterface(self):
		return self.classID[-1][2]


	def wasInstr(self):
		return self.isInstr


	def getLine(self, instr, tok):
		lineNumber = 1
		isFound = False
		instr = ' '.join(instr.split())
		code = ""
		with open(self.filename, 'r') as f:
			while True:
				line = f.readline()
				if line == '':
					break
				line = FileReader.removeComments(line)	# to accelerate the process
				line = ' '.join(line.split())
				code += ' ' + line
				if FileReader.clearLine(instr) in code:
					if tok[R.NBOBRACES] == self.nbOBraces and tok[R.NBCBRACES] == self.nbCBraces:
						isFound = True
						break
				self.updateID(line+'\n')
				lineNumber += 1
		self.resetCursor()
		if isFound == False:
			lineNumber = -1
		return lineNumber


