#!/usr/bin/python3

from FileReader import *
from Parser import *
from R import *
import os

class Display():
	@staticmethod
	def showResults(results, nb, Reader, packageDir, validation, nr):
		if R.CRITICAL in nb and nb[R.CRITICAL] > 0:
			print("\033[1m\033[91m[-] %d file(s) have CRITICAL issue(s)\033[0m\033[0m" % nb[R.CRITICAL])
		if R.OK in nb and nb[R.OK] > 0:
			print("\033[1m\033[92m[+] %d file(s) have GOOD pratice(s)\033[0m\033[0m" % nb[R.OK])
		if R.NOTHING in nb and nb[R.NOTHING] > 0:
			print("\033[1m\033[37m[*] %d file(s) have NOTHING to report\033[0m\033[0m" % nb[R.NOTHING])
		if R.WARNING in nb and nb[R.WARNING] > 0:
			print("\033[1m\033[33m[!] %d file(s) have WARNING(S)\033[0m\033[0m" % nb[R.WARNING])

		if validation:
			print("")
			print("DO YOU WANT RESET THE COUNTERS? [y/n]")
			temp = "a"
			while temp != "y" and temp != "n":
				temp = input()
				if (temp == "y"):
					try:
						os.remove("temp" + str(nr))
					except:
						a=0
			print("")

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
			kind = "[EXTERNAL]"
			if ((packageDir != None) and (packageDir in file[0])) or ("AndroidManifest.xml" in file[0]):
				kind = "[INTERNAL]"

			# CRITICAL
			if R.CRITICAL in file[1] and len(file[1][R.CRITICAL]) > 0:
				fileReader = Reader(file[0], False)
				print("%s\033[91m\033[01m >>>\033[0m %s" % (kind, file[0])) 
				lineNumber = -1
				lastmsg = ""
				for i in file[1][R.CRITICAL]:
					if i[R.INSTR] != '':
						lineNumber = fileReader.getLine(i[R.INSTR], i)
					else:
						lineNumber = -1

					if lastmsg != i[R.ERRORMSG]:
						print("\033[91m* %s\033[0m" % i[R.ERRORMSG])
						lastmsg = i[R.ERRORMSG]

					if lineNumber != -1:
						msg = "at line " + str(lineNumber)
					else:
						if i[R.INSTR] == '':
							msg = "no line to display"
						else:
							msg = "line not found"

					print("\033[91m- \033[1m{0}\033[0m\033[91m: '{1}' \033[0m".format(msg, i[R.INSTR]))
					print("")
					if validation:
						os.system("gedit +%s %s" % (lineNumber, file[0]))
						print("TRUE POSITIVE? [y/n]")
						temp = "a"
						while temp != "y" and temp != "n":
							temp = input()
							if (temp == "y"):
								counterCriticalTP = counterCriticalTP + 1
							if (temp == "n"):
								counterCriticalFP = counterCriticalFP + 1
					print("")
			# WARNING
			if R.WARNING in file[1] and len(file[1][R.WARNING]) > 0:
				fileReader = Reader(file[0], False)
				print("%s\033[33m\033[01m >>>\033[0m %s" % (kind, file[0]))
				lineNumber = -1
				lastmsg = ""
				for i in file[1][R.WARNING]:
					if i[R.INSTR] != '':
						lineNumber = fileReader.getLine(i[R.INSTR], i)
					else:
						lineNumber = -1

					if lastmsg != i[R.ERRORMSG]:
						print("\033[33m* %s\033[0m" % i[R.ERRORMSG])
						lastmsg = i[R.ERRORMSG]

					if lineNumber != -1:
						msg = "at line " + str(lineNumber)
					else:
						if i[R.INSTR] == '':
							msg = "no line to display"
						else:
							msg = "line not found"
					print("\033[33m- \033[1m%s\033[0m\033[33m: '%s' \033[0m" % (msg, i[R.INSTR]))
					print("")
					if validation:
						os.system("gedit +%s %s" % (lineNumber, file[0]))
						print("TRUE POSITIVE? [y/n]")
						temp = "a"
						while temp != "y" and temp != "n":
							temp = input()
							if (temp == "y"):
								counterWarningTP = counterWarningTP + 1
							if (temp == "n"):
								counterWarningFP = counterWarningFP + 1
					print("")

			# OK
			if R.OK in file[1] and len(file[1][R.OK]) > 0:
				fileReader = Reader(file[0], False)
				print("%s\033[92m\033[01m >>>\033[0m %s" % (kind, file[0]))
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
					print("\033[92m- \033[1m%s\033[0m\033[92m: '%s' \033[0m" % (msg, i[R.INSTR]))
					print("")
					if validation:
						os.system ("gedit +%s %s" % (lineNumber, file[0]))
						print ("TRUE POSITIVE? [y/n]")
						temp = "a"
						while temp != "y" and temp != "n":
							temp = input()
							if (temp == "y"):
								counterOkTP = counterOkTP + 1
							if (temp == "n"):
								counterOkFP = counterOkFP + 1
				print("")

		if validation:
			print ("CRITICAL FALSE POSITIVE %s" % (counterCriticalFP))
			print ("CRITICAL TRUE POSITIVE %s" % (counterCriticalTP))
			print ("WARNING FALSE POSITIVE %s" % (counterWarningFP))
			print ("WARNING TRUE POSITIVE %s" % (counterWarningTP))
			print ("OK FALSE POSITIVE %s" % (counterOkFP))
			print ("OK TRUE POSITIVE %s" % (counterOkTP))
			print("")
			if (counterCriticalTP+counterCriticalFP) == 0:
				print("THERE ARE NO CRITICAL DATA")
			else:
				print ("CRITICAL PRECISION %s" % (counterCriticalTP/(counterCriticalTP+counterCriticalFP)))
			if (counterWarningTP+counterWarningFP) == 0:
				print("THERE ARE NO WARNING DATA")
			else:
				print ("WARNING PRECISION %s" % (counterWarningTP/(counterWarningTP+counterWarningFP)))
			if (counterOkTP+counterOkFP) == 0:
				print("THERE ARE NO OK DATA")
			else:
				print ("OK PRECISION %s" % (counterOkTP/(counterOkTP+counterOkFP)))

			out_file = open("temp"+str(nr), "w+")
			out_file.write(str(counterCriticalFP)+"\n")
			out_file.write(str(counterCriticalTP)+"\n")
			out_file.write(str(counterOkFP)+"\n")
			out_file.write(str(counterOkTP)+"\n")
			out_file.write(str(counterWarningFP)+"\n")
			out_file.write(str(counterWarningTP)+"\n")
			out_file.close()
