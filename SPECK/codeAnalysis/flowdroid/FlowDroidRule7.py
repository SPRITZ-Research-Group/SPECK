#!/usr/bin/python3
import subprocess, os.path, copy, sys
from R import *
from Parser import *
from FlowDroid import *

class FlowDroidRule7():

	def __init__(self, flowDroid, apk, sources, sinks, errMsg, verboseDeveloper):
		self.FlowDroid = flowDroid
		self.sources = sources
		self.sinks = sinks
		self.errMsg = errMsg
		self.verboseDeveloper = verboseDeveloper
		self.apk = apk

	def start(self, results, statFiles):
		results, statFiles = self.GoodButBad(results, statFiles)
		results, statFiles = self.BadNotDetected(results, statFiles)
		return results, statFiles

	def getToken(self, sink):
		paths = Parser.getAllPath(self.apk.replace(".apk", "/"), 'java')

		p = self.FlowDroid.getPath(paths, sink)
		m = self.FlowDroid.getMethodSource(sink)
		keyword = "setWebViewClient("

		if p != None:
			fr = FileReader(p)
			line, tok = fr.getNextInstruction()
			while line != '':
				if tok[R.PATH] == m:
					if keyword in tok[R.INSTR]:
						fr.close()
						return tok
						break


				line, tok = fr.getNextInstruction()
			fr.close()

		return None

	def GoodButBad(self, results, statFiles):
		'''for e in self.sinks:
			print("-> ", e)

		for e in self.sources:
			print("* ", e)'''

		results_cpy = copy.deepcopy(results)

		index = 0
		for file in results_cpy:
			severity = self.FlowDroid.getErrorSeverity(file[1])

			for err in file[1][severity]:
				bad_location = err[R.PATH]
				mSources = self.FlowDroid.getAllMethodSources(self.sources)
				
				srcIndex = 0
				for elem in mSources:
					# check if method location match
					if bad_location == elem:							
						results, statFiles = self.FlowDroid.Bad2Good(results, statFiles, index, err, severity, self.verboseDeveloper)
						if len(results[index][1][severity]) == 0:
							statFiles[severity] -= 1
						break

					srcIndex += 1
			index += 1

		'''In = []
		for s in self.sinks:
			tok = self.getToken(s)
			In.append(self.getToken(s))'''

		return results, statFiles

	def BadNotDetected(self, results, statFiles):
		return results, statFiles





		