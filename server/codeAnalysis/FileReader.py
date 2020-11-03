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
		if (toParse):
			self.parse()

	def parse(self):
		code = ""
		with open(self.filename, 'r') as f:
			while True:
				line = f.readline()

				if self.package == "":
					if "package" in line:
						self.package = line.split(" ")[1].replace(";", "")

				if (line == ''):
					break

				line = FileReader.sanitizeOverride(line)

				code += line

		code = FileReader.clearComment(code)
		code = ' '.join(code.split())
		code = FileReader.clearString(code)

		# write data in temporary file
		self.tmp.write(code)
		self.tmp.seek(0)

	@staticmethod
	def sanitizeOverride(line):
		cpy = line.strip()
		if (cpy.startswith('@')):
			line = ""
			for c in cpy:
				if c == '{':
					line += '{'
				elif c == '}':
					line += '}'
		return line

	@staticmethod
	def clearComment(code):
		code = code.split('"')

		for i in range(0, len(code)):
			if ("//" in code[i]) and (i%2 == 0):
				code[i] = code[i].replace("//", "\n//")

		code = '"'.join(code)

		o = code.find("\n//")
		c = code.find("\n", o+1)
		while(o != -1 and c != -1):
			code = code.replace(code[o:c+1], '')
			o = code.find("\n//", c+1)
			c = code.find("\n", o+1)

		return code

	@staticmethod
	def clearString(code):
		code = code.split('"')

		for i in range(0, len(code)):
			if i%2 == 0:
				code[i] = code[i].replace(";", ";\n").replace("{", "\n{\n").replace("}", "\n}\n").replace("/*", '\n/*\n').replace("*/", '\n*/\n').replace("\n\n","\n")
			else:
				code[i] = code[i].replace(";", "").replace("{", "").replace("}", "").replace("/*", '').replace("*/", '')

		return '"'.join(code)

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

	def updateID(self, line):
		line = FileReader.clearLine(line)

		# UPDATE BLOCKID AND ROOTID
		for c in line:
			if (c == '{'):
				self.nbOBraces += 1
				self.oBrace += 1
				self.hasChanged = True
			elif (c == '}'):
				self.nbCBraces += 1
				self.cBrace += 1
				self.hasChanged = True

			self.blockID = self.oBrace - self.cBrace
			if (self.hasChanged and self.blockID == 0):
				self.rootID += 1
				self.oBrace = 0
				self.cBrace = 0
				self.hasChanged = False
				
	def getNextInstruction(self):
		self.isInstr = False
		line = self.tmp.readline()

		if (line == ''):
			token = self.constructToken(line)
			return line, token

		line = line.strip()

		self.updateID(line)

		# Try / Catch
		if (line.startswith('try')):
			self.inTry = True
		elif (line.startswith('catch')) or (line.startswith('finally')):
			self.inTry = False

		# Commentary
		elif (line.startswith("/*")):
			line = '\n'
			self.inCommentary = True
		elif (line.startswith("*/")):
			line = '\n'
			self.inCommentary = False
		elif (line.startswith("//")):
			line = '\n'
		elif (self.inCommentary):
			line = '\n'

		# Empty line
		elif (line == ''):
			line = '\n'

		# Conditions
		elif (line.startswith('default') 
			or line.startswith('case') 
			or line.startswith('switch')): 
			pass

		# Special character
		elif (line.startswith('@')):
			line = '\n'
			pass

		# Conditions
		elif (line.startswith('if')
			or line.startswith('else')):
			pass

		# Loop
		elif (line.startswith('for')
			or line.startswith('while')):
			pass

		# Class
		elif 'class ' in line and ';' not in line:
			self.classID.append([self.clssId, self.blockID+1, False])
			self.className.append(line.split("class ")[1].split(" ")[0].split("(")[0])
			self.clssId += 1
			pass

		elif 'interface ' in line and ';' not in line:
			self.classID.append([self.clssId, self.blockID+1, True])
			self.className.append(line.split("interface ")[1].split(" ")[0].split("(")[0])
			self.clssId += 1
			pass

		# Block
		elif (line.startswith('{')):
			pass

		elif (line.startswith('}')):
			if (len(self.classID) > 1 and self.classID[-1][1] > self.blockID):
				del self.classID[-1]
				del self.className[-1]
			if (len(self.funcID) > 1 and self.funcID[-1][1] > self.blockID):
				del self.funcID[-1]
				del self.funcName[-1]
			pass

		# Function
		elif (';' not in line 
			and '=' not in line
			and '(' in line
			and ')' in line):
			self.funcID.append([self.fID, self.blockID+1])
			self.funcName.append(line.split("(")[0].split(" ")[-1])
			self.fID += 1
			pass

		# Instruction & various
		else:
			self.isInstr = True
			pass

		token = self.constructToken(line)

		'''print("token: ", token[R.PATH])
		print("line  : ", line)
		print("class : ", self.className)
		print("func  : ", self.funcName)
		print("pkg   : ", self.package)'''

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
		threshold = 100

		with open(self.filename, 'r') as f:
			while True:
				line = f.readline()
				if (line == ''):
					break

				# to accelerate the process
				line = FileReader.clearLine(line)
				line = ' '.join(line.split())
				code += ' ' + line

				if FileReader.clearLine(instr) in code:
					if (tok[R.NBOBRACES] == self.nbOBraces
						and tok[R.NBCBRACES] == self.nbCBraces):
	
						isFound = True
						break

				self.updateID(line+'\n')
				lineNumber += 1

		self.resetCursor()

		if isFound == False:
			lineNumber = -1

		return lineNumber



