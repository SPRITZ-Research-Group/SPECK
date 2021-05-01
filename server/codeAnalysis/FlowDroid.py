#!/usr/bin/python3
import subprocess, os.path, copy, sys
sys.path.insert(0, 'codeAnalysis/flowdroid/')
from R import *
from Parser import *
from FileReader import *
from FlowDroidRule1 import *
from FlowDroidRule7 import *
from FlowDroidRule9 import *
from FlowDroidRule17 import *
from FlowDroidRule20 import *
from FlowDroidRule24 import *
from FlowDroidRule27 import *
from FlowDroidRule28 import *
from FlowDroidRule32 import *
from FlowDroidRule35 import *
import time

DIR = "codeAnalysis/flowdroid/"
PREFIX = "SourcesAndSinksRule"
EXT = ".txt"

class FlowDroid():
	ID = "id"
	TYPE = "type"
	SINK = 0
	SOURCE = 1

	INVOKE = "invoke"
	METHOD = "method"
	FLOW = "flow"

	def __init__(self, rule, apk, platform, verbose, verboseDeveloper, errMsg):
		self.rule = rule
		self.apk = apk
		self.platform = platform
		self.verbose = verbose
		self.verboseDeveloper = verboseDeveloper
		self.errMsg = errMsg
		self.srcNsink = DIR + PREFIX + str(rule) + EXT
		self.sources = None
		self.sinks = None

		self.fct = [FlowDroidRule1, None, None, None, None, None, FlowDroidRule7, None, FlowDroidRule9, None,
					None, None, None, None, None, None, FlowDroidRule17, None, None, FlowDroidRule20, None, None, None, FlowDroidRule24,
					None, None, FlowDroidRule27, FlowDroidRule28, None, None, None, FlowDroidRule32, None, None, FlowDroidRule35]

		if os.path.isfile(self.srcNsink) and os.path.isfile(apk):
		# if os.path.isfile(self.srcNsink):
			if self.verbose:
				print("\033[36m[?] FlowDroid is running...\033[0m")
			self.getSrcNSink()
		else:
			if self.verbose:
				print("\033[36m[?] FlowDroid can't be used\033[0m\n")

	def getSrcNSink(self):
		out = subprocess.Popen(['java', '-jar', DIR + 'soot-infoflow-cmd-jar-with-dependencies.jar',
										'-a', self.apk,
										'-p', self.platform,
										'-s', self.srcNsink,
										'--mergedexfiles',
										'--aliasflowins',
										'--aplength', '1',
										'--noexceptions',
										'--nostatic',
										'--timeout', '200',
										'--resulttimeout', '200'],
           stdout=subprocess.PIPE,
           stderr=subprocess.STDOUT)

		stdout = []
		tStart = time.time()
		while True :
			data = out.stdout.readline().decode().strip()
			stdout.append(data)
			# print(data)

			if ("leaks" in data and "Found" in data):
				subprocess.call("ps -a | grep \"soot-infoflow-cmd-jar-with-dependencies\" | awk '{print $1}' | xargs kill 2> /dev/null;", shell=True)
				break

			if not data:
				print("No more data!")
				break

		Id = 0
		self.sinks = []
		self.sources = []
		for line in stdout:
			elem = {}
			if "The sink " in line:
				elem[FlowDroid.ID] = Id
				elem[FlowDroid.TYPE] = FlowDroid.SINK
				elem[FlowDroid.INVOKE] = line.split("The sink ")[1].split(" in method ")[0]
				elem[FlowDroid.METHOD] = line.split("The sink ")[1].split(" in method ")[1].split(" was called with values from the following sources:")[0]
				self.sinks.append(elem)
				Id += 1
			elif "- - " in line:
				elem[FlowDroid.FLOW] = self.sinks[-1][FlowDroid.ID]
				elem[FlowDroid.TYPE] = FlowDroid.SOURCE
				elem[FlowDroid.INVOKE] = line.split("- - ")[1].split(" in method ")[0]
				elem[FlowDroid.METHOD] = line.split("- - ")[1].split(" in method ")[1]
				self.sources.append(elem)

		if self.verbose:
			print("\033[36m[?] FlowDroid has finished\033[0m\n")

	def run(self, results, statFiles):
		if self.sources != None and self.fct[self.rule-1] != None:
			f = self.fct[self.rule-1](FlowDroid, self.apk, self.sources, self.sinks, self.errMsg, self.verboseDeveloper)
			return f.start(results, statFiles)
		else:
			return results, statFiles

	@staticmethod
	def getSinkById(Id, sinks):
		for s in sinks:
			if s[FlowDroid.ID] == Id:
				return s

	@staticmethod
	def getMethodSource(source):
		method = source[FlowDroid.METHOD]
		pkg = method.split(":")[0].replace("<", "")
		fct = method.split(">")[0].split(" ")[-1].split("(")[0]

		if fct.endswith("<init"):
			fct = fct.replace("<init", pkg.split(".")[-1])

		return pkg + '.' + fct

	@staticmethod
	def getAllMethodSources(sources):
		res = []
		for elem in sources:
			res.append(FlowDroid.getMethodSource(elem))
		return res

	@staticmethod
	def getSinkMethod(sinks, Id):
		for s in sinks:
			if s[FlowDroid.ID] == Id:
				return s[FlowDroid.INVOKE].split("<")[1].split(">")[0].split(" ")[-1].split("(")[0]
		return ""

	@staticmethod
	def getCompleteSinkMethod(sinks, Id):
		for s in sinks:
			if s[FlowDroid.ID] == Id:
				res = s[FlowDroid.METHOD].split(":")[0].replace("<", "") + '.' + s[FlowDroid.METHOD].split(" ")[-1].split("(")[0]
				if res.endswith(".<init>"):
					res = res.replace(".<init>", "")
					res = res + "." + res.split(".")[-1]
				return res
		return ""

	@staticmethod
	def getArgInvoked(source, arg):
		invoke = source[FlowDroid.INVOKE]
		args = invoke.split(")")[-2].split("(")[1].split(",")

		if len(args) > arg:
			return args[arg]

		return None

	@staticmethod
	def getErrorSeverity(errors):
		if R.CRITICAL in errors:
			return R.CRITICAL
		else:
			return R.WARNING

	@staticmethod
	def getPath(paths, b):
		filename = b[FlowDroid.METHOD].split(":")[0].replace("<", "").split(".")[-1] + ".java"
		for f in paths:
			if f.endswith(filename):
				return f
		return None

	@staticmethod
	def delete(results, statFiles, tokens, severity):
		results_cpy = copy.deepcopy(results)
		index = 0
		for file in results_cpy:
			if severity in list(file[1].keys()):
				for elem in file[1][severity]:
					for t in tokens:
						if elem[R.PATH] == t[R.PATH]:
							results[index][1][severity].remove(elem)

					if len(results[index][1][severity]) == 0:
						statFiles[severity] -= 1
				index += 1

		return results, statFiles


	@staticmethod
	def Bad2Good(results, statFiles, index, err, severity, verboseDeveloper):
		# del bad one
		filename = results[index][0]
		results[index][1][severity].remove(err)

		# add good one
		good = err
		if not verboseDeveloper:
			if len(results[index][1][R.OK]) == 0:
				statFiles[R.OK] += 1
			results[index][1][R.OK].append(good)

		return results, statFiles

	@staticmethod
	def appendBadToken(rule, errMsg, tok, results, statFiles, path, severity):
		wasFound = False
		for file in results:
			if file[0] == path:
				# check if error was not already found
				found = False
				for elem in file[1][severity]:
					if elem[R.PATH] == tok[R.PATH] and elem[R.INSTR] == tok[R.INSTR]:
						found = True
						wasFound = True
						break

				if not found:
					if len(file[1][severity]) == 0:
						statFiles[severity] += 1
					file[1][severity].append(tok)
					wasFound = True
					break

		tok[R.ERRORTYPE] = severity
		if rule == 1 or rule == 7 or rule == 9 or rule == 20 or rule == 24 or rule == 27 or rule == 32 or rule == 35:
			tok[R.ERRORMSG] = errMsg[0]

		if not wasFound:
			data = {}
			data[severity] = [tok]
			results.append([ path, data ])
			statFiles[severity] += 1

		return results, statFiles

	@staticmethod
	def GoodButBad(results, statFiles, sources, verboseDeveloper):
		results_cpy = copy.deepcopy(results)

		index = 0
		for file in results_cpy:
			severity = FlowDroid.getErrorSeverity(file[1])

			for err in file[1][severity]:
				bad_location = err[R.PATH]
				mSources = FlowDroid.getAllMethodSources(sources)

				'''print("bad loc: ", bad_location)
				print("sources: ", mSources)'''

				srcIndex = 0
				for elem in mSources:
					# check if method location match
					if bad_location == elem:
						results, statFiles = FlowDroid.Bad2Good(results, statFiles, index, err, severity, verboseDeveloper)
						if len(results[index][1][severity]) == 0:
							statFiles[severity] -= 1
						break

					srcIndex += 1
			index += 1

		return results, statFiles

	@staticmethod
	def Good2Bad(results, statFiles, index, err, severity, verboseDeveloper):
		# del bad one
		filename = results[index][0]
		results[index][1][R.OK].remove(err)

		# add good one
		good = err
		if not verboseDeveloper:
			if len(results[index][1][severity]) == 0:
				statFiles[severity] += 1
			results[index][1][severity].append(good)

		return results, statFiles

	@staticmethod
	def BadButGood(results, statFiles, sources, verboseDeveloper, severity):
		results_cpy = copy.deepcopy(results)

		index = 0
		for file in results_cpy:
			if not R.OK in list(file[1].keys()):
				continue
			for err in file[1][R.OK]:
				good_location = err[R.PATH]
				mSources = FlowDroid.getAllMethodSources(sources)

				srcIndex = 0
				for elem in mSources:
					# check if method location match
					if good_location == elem:
						results, statFiles = FlowDroid.Good2Bad(results, statFiles, index, err, severity, verboseDeveloper)
						if len(results[index][1][R.OK]) == 0:
							statFiles[R.OK] -= 1
						break

					srcIndex += 1
			index += 1

		return results, statFiles
