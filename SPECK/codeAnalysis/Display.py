#!/usr/bin/python3

from FileReader import *
from XmlReader import *
from Parser import *
from R import *
import os


class Display():

	@staticmethod
	def showResults(results, nb, Reader, packageDir, validation, nr):
		all_null = True
		for key in nb:
			if nb[key] > 0:
				all_null = False
				break

		if all_null:
			print("\033[1m\033[92m[+] No violation has been found.\033[0m\033[0m")
			return

		if R.CRITICAL in nb and nb[R.CRITICAL] > 0:
			print(f"\033[1m\033[91m[-] {nb[R.CRITICAL]} file(s) have CRITICAL issue(s)\033[0m\033[0m")
		if R.OK in nb and nb[R.OK] > 0:
			print(f"\033[1m\033[92m[+] {nb[R.OK]} file(s) have GOOD pratice(s)\033[0m\033[0m")
		if R.NOTHING in nb and nb[R.NOTHING] > 0:
			print(f"\033[1m\033[37m[*] {nb[R.NOTHING]} file(s) have NOTHING to report\033[0m\033[0m")
		if R.WARNING in nb and nb[R.WARNING] > 0:
			print(f"\033[1m\033[33m[!] {nb[R.WARNING]} file(s) have WARNING(S)\033[0m\033[0m")
		if R.NA in nb and nb[R.NA] > 0:
			print(f"\033[1m\033[91m[!] {nb[R.NA]} file(s) DO NOT RESPECT THE RULE\033[0m\033[0m")

		try:
			in_file = open("temp" + str(nr), "r")
			text = in_file.readlines()
			counterCriticalFP = int(text[0])
			counterCriticalTP = int(text[1])
			counterOkFP = int(text[2])
			counterOkTP = int(text[3])
			counterWarningFP = int(text[4])
			counterWarningTP = int(text[5])
			in_file.close()
		except:
			counterCriticalFP = 0
			counterCriticalTP = 0
			counterOkFP = 0
			counterOkTP = 0
			counterWarningFP = 0
			counterWarningTP = 0

		for file in results:
			
			# Handle Reader
			if Reader == None:
				extension = file[0].split('.')[-1]
				if extension == "xml":
					Reader = XmlReader
				else:
					Reader = FileReader
			kind = "[EXTERNAL]"
			if ((packageDir != None) and (packageDir in file[0])) or (".xml" in file[0]):
				kind = "[INTERNAL]"

			# NA
			if R.NA in file[1] and len(file[1][R.NA]) > 0:
				fileReader = Reader(file[0], False)
				print(f"{kind}\033[93m\033[01m >>>\033[0m {file[0]}")	 # len(file[1][R.NA])
				lineNumber = -1
				lastmsg = ""

				for i in file[1][R.NA]:
					if i[R.INSTR] != '':
						lineNumber = fileReader.getLine(i[R.INSTR], i)
					else:
						lineNumber = -1
					
					if not R.ERRORMSG in i:
						i[R.ERRORMSG] = " "

					if lastmsg != i[R.ERRORMSG]:
						print(f"\033[93m* {i[R.ERRORMSG]}\033[0m")
						lastmsg = i[R.ERRORMSG]

					if lineNumber != -1:
						msg = "at line " + str(lineNumber)
					else:
						if i[R.INSTR] == '':
							msg = "no line to display"
						else:
							msg = "line not found"

					print(f"\033[93m- \033[1m{msg}\033[0m\033[93m: '{i[R.INSTR]}' \033[0m")
					print("")
					
			# CRITICAL
			if R.CRITICAL in file[1] and len(file[1][R.CRITICAL]) > 0:
				fileReader = Reader(file[0], False)
				print(f"{kind}\033[91m\033[01m >>>\033[0m {file[0]}")	 # len(file[1][R.CRITICAL])
				lineNumber = -1
				lastmsg = ""
				for i in file[1][R.CRITICAL]:
					if i[R.INSTR] != '':
						lineNumber = fileReader.getLine(i[R.INSTR], i)
					else:
						lineNumber = -1
					if lastmsg != i[R.ERRORMSG]:
						print(f"\033[91m* {i[R.ERRORMSG]}\033[0m")
						lastmsg = i[R.ERRORMSG]
					if lineNumber != -1:
						msg = "at line " + str(lineNumber)
					else:
						if i[R.INSTR] == '':
							msg = "no line to display"
						else:
							msg = "line not found"

					print(f"\033[91m- \033[1m{msg}\033[0m\033[91m: '{i[R.INSTR]}' \033[0m")
					print("")
					
			# WARNING
			if R.WARNING in file[1] and len(file[1][R.WARNING]) > 0:
				fileReader = Reader(file[0], False)
				print(f"{kind}\033[33m\033[01m >>>\033[0m {file[0]}")
				lineNumber = -1
				lastmsg = ""
				for i in file[1][R.WARNING]:
					if i[R.INSTR] != '':
						lineNumber = fileReader.getLine(i[R.INSTR], i)
					else:
						lineNumber = -1

					if lastmsg != i[R.ERRORMSG]:
						print(f"\033[33m* {i[R.ERRORMSG]}\033[0m")
						lastmsg = i[R.ERRORMSG]

					if lineNumber != -1:
						msg = "at line " + str(lineNumber)
					else:
						if i[R.INSTR] == '':
							msg = "no line to display"
						else:
							msg = "line not found"
					print(f"\033[33m- \033[1m{msg}\033[0m\033[33m: '{i[R.INSTR]}' \033[0m")
					print("")

			# OK
			if R.OK in file[1] and len(file[1][R.OK]) > 0:
				fileReader = Reader(file[0], False)
				print(f"{kind}\033[92m\033[01m >>>\033[0m {file[0]}")
				lineNumber = -1
				for i in file[1][R.OK]:
					if i[R.INSTR] != '':
						lineNumber = fileReader.getLine(i[R.INSTR], i)
					else:
						lineNumber = -1
						
					if lineNumber != -1:
						msg = "at line " + str(lineNumber)
					else:
						if i[R.INSTR] == '':
							msg = "no line to display"
						else:
							msg = "line not found"
					print(f"\033[92m- \033[1m{msg}\033[0m\033[92m: '{i[R.INSTR]}' \033[0m")
					print("")


