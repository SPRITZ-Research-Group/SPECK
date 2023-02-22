#!/usr/bin/python3

import sys, argparse
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
from Rule33 import *
from Rule34 import *
from Rule35 import *


# MAIN
if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='Code analysis tests')
	parser.add_argument('-d','--directory', help="App directory name", required=True)
	parser.add_argument('-r','--rules',nargs='+', help="rules numbers", required=True)
	parser.add_argument('-f','--flowdroid', help="Use FlowDroid to detect false positive / negative", action='store_true')
	parser.add_argument('-p','--platform', help="Android SDK platform folder")
	parser.add_argument('-z','--validation',action='store_true', help="Open files to view the Code")
	args = parser.parse_args()

	print(args.validation)
	print(args.validation)
	print(args.validation)
	print(args.validation)
	print(args.validation)
	print(args.validation)
	print(args.validation)

	if args.flowdroid and args.platform is None:
		parser.error("--flowdroid requires --platform")

	directory = args.directory

	func = [Rule1, Rule2, Rule3, Rule4, Rule5, Rule6, Rule7,
				Rule8, Rule9, Rule10, Rule11, Rule12, Rule13, Rule14,
				Rule15, Rule16, Rule17, Rule18, Rule19, Rule20, Rule21,
				Rule22, Rule23, Rule24, Rule25, Rule26, Rule27, Rule28,
				Rule29, Rule30, Rule31, Rule32, Rule33, Rule34, Rule35]

	resExpected = [[6,7], [2,3], [2,0], [2,0], [4,6], [2,0], [2,3], [1,1], [4,5], [2,0],
				   [1,0], [1,1], [0,1], [0,1], [1,0], [1,0], [2,3], [2,0], [1,1], [4,0],
				   [2,0], [1,2], [3,0], [1,1], [2,1], [1,0], [1,1], [2,1], [1,0], [2,0],
				   [4,4], [2,1], [2,0], [1,0], [2,2]]

	for r in args.rules:
		print(f"\n\033[93m[?] RULE N°{int(r)} -> expected results: {resExpected[int(r)-1][0]} BAD / {resExpected[int(r)-1][1]} GOOD\033[0m")
		rulefct = func[int(r)-1](directory+'/rule'+str(r)+'/', True, False, None, args.flowdroid, args.platform, args.validation)
		rulefct.run()


	