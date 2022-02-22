#!/usr/bin/python3

import os, sys, subprocess, glob, argparse, time
os.chdir(os.path.dirname(__file__))
sys.path.insert(0, 'codeAnalysis/')
sys.path.insert(0, 'codeAnalysis/Rules/')

from Rule1 import *
from Rule2 import *
from Rule3 import *
from Rule4 import *
from Rule5 import *
from Rule6 import *
from Rule7 import *
from Rule8 import *
from Rule9 import *
from Rule10 import *
from Rule11 import *
from Rule12 import *
from Rule13 import *
from Rule14 import *
from Rule15 import *
from Rule16 import *
from Rule17 import *
from Rule18 import *
from Rule19 import *
from Rule20 import *
from Rule21 import *
from Rule22 import *
from Rule23 import *
from Rule24 import *
from Rule25 import *
from Rule26 import *
from Rule27 import *
from Rule28 import *
from Rule29 import *
from Rule30 import *
from Rule31 import *
from Rule32 import *
from Storage import *

class Scan():
	def __init__(self, directory, rules, timeout, good, flowdroid, platform, quiet, database=None):
		self.database=database
		self.quiet = quiet
		self.good = good
		self.flowdroid = flowdroid
		self.platform = platform
		if rules == None:
			self.rules = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', 
					   '12', '13', '14', '15', '16', '17', '18', '19', '20', '21', '22',  
					   '23', '24','25', '26', '27', '28', '29', '30', '31', '32']
		else:
			self.rules = rules

		if timeout == None:
			self.timeout = 180
		else:
			self.timeout = timeout

		if os.path.isdir(directory):
			self.directory = directory
		elif directory.endswith(".apk"):
			self.extract(directory)
		else:
			self.directory = None

	def extract(self, file):
		print("\033[44m[+] Extracting %s\033[0m" % file.split('/')[-1])

		try:
			subprocess.call("./apk2src/decompiler.sh "+ file, shell=True, timeout=self.timeout)
		except KeyboardInterrupt:
			sys.exit(0)
		except:
			subprocess.call("ps -a | grep \"apk2src\" | awk '{print $1}' | xargs kill 2> /dev/null;", shell=True)

		self.directory = file.replace('.apk', '')
		if not (os.path.isfile(self.directory+"/resources/AndroidManifest.xml")):
			print("\033[31m[-] {0} extraction failed\033[0m".format(file.split('/')[-1]))
			with open('errors.txt', 'a+') as x:
				x.write("extraction failed: {0}\n".format(file.split('/')[-1]))
			self.directory = None
		else:
			print("\033[32m[+] %s extracted\033[0m" % file.split('/')[-1])

	def analyse(self):
		os.system('clear')

		print("\033[44m[!] Analysing {0}\033[0m".format(self.directory.split('/')[-1]))

		func = [Rule1, Rule2, Rule3, Rule4, Rule5, Rule6, Rule7,
				Rule8, Rule9, Rule10, Rule11, Rule12, Rule13, Rule14,
				Rule15, Rule16, Rule17, Rule18, Rule19, Rule20, Rule21,
				Rule22, Rule23, Rule24, Rule25, Rule26, Rule27, Rule28,
				Rule29, Rule30, Rule31, Rule32]


		for rule in self.rules:
			ruleStart = time.time()
			rulefct = func[int(rule)-1](self.directory, self.database, True, not self.good, StoreJson(), self.flowdroid, self.platform, quiet = self.quiet)
			rulefct.run()
			ruleEnd = time.time()
			apk = rulefct.directory
			if rulefct.directory.endswith("/"):
				apk = rulefct.directory[:-1]
			StoreJson.store("rulestats",{"apk": apk, "rule": rule, "start": ruleStart, "end": ruleEnd}, self.database)

	def run(self):
		if self.directory != None:
			self.analyse()


# MAIN
if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='Analyse an application')
	parser.add_argument('-s','--source', help="App directory / Apk file", required=True)
	parser.add_argument('-r','--rules', nargs='+', help="rules numbers")
	parser.add_argument('-t','--timeout', help="Time before killing bash process", type=int)
	parser.add_argument('-g','--good', help="Display good practices", action='store_true')
	parser.add_argument('-f','--flowdroid', help="Use FlowDroid to detect false positive / negative", action='store_true')
	parser.add_argument('-p','--platform', help="Android SDK platform folder")
	parser.add_argument('-q', '--quiet', help="Output to parse", action='store_true')
	parser.add_argument('-D', '--database', help="database where to save all violations")
	args = parser.parse_args()

	if args.flowdroid and args.platform is None:
		parser.error("--flowdroid requires --platform")

	scan = Scan(args.source, args.rules, args.timeout, args.good, args.flowdroid, args.platform, args.quiet, args.database)
	scan.run()
