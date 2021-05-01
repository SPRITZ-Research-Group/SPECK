#!/usr/bin/python3
import subprocess, os.path, copy, sys
from FlowDroid import *

class FlowDroidRule20():

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

	def GoodButBad(self, results, statFiles):
		return results, statFiles

	def BadNotDetected(self, results, statFiles):
		'''print("20 =====")
		for e in self.sinks:
			print("-> ", e)

		for e in self.sources:
			print("* ", e)'''

		paths = Parser.getAllPath(self.apk.replace(".apk", "/"), 'java')

		for s in self.sinks:
			p = self.FlowDroid.getPath(paths, s)
			m = self.FlowDroid.getMethodSource(s)

			'''print("path: ", p)
			print("method: ", m)'''

			if p != None:
				fr = FileReader(p)
				line, tok = fr.getNextInstruction()
				while line != '':
					if tok[R.PATH] == m:
						results, statFiles = self.FlowDroid.appendBadToken(20, self.errMsg, tok, results, statFiles, p, R.CRITICAL)
						break


					line, tok = fr.getNextInstruction()
				fr.close()

		return results, statFiles





		