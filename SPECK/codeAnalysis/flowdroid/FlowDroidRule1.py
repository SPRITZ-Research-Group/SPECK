#!/usr/bin/python3
import subprocess, os.path, copy, sys
from R import *
from Parser import *
from FlowDroid import *

class FlowDroidRule1():

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

	def getFctKeywordRule1(self, b):
		if "<android.content.Intent: android.content.Intent setAction(java.lang.String)>" in b[self.FlowDroid.INVOKE]:
			return  "setAction("
		else:
			return "new Intent("

	def GoodButBad(self, results, statFiles):
		results_cpy = copy.deepcopy(results)

		index = 0
		for file in results_cpy:
			severity = self.FlowDroid.getErrorSeverity(file[1])

			for err in file[1][severity]:
				bad_location = err[R.PATH]
				mSources = self.FlowDroid.getAllMethodSources(self.sources)
				#print("f : ", file[0])
				#print("Bad location : ", bad_location)
				#print("Src location : ", mSources)
				srcIndex = 0
				for elem in mSources:
					# check if method location match
					if bad_location == elem:
						# check if arg used match
						if self.FlowDroid.getArgInvoked(self.sources[srcIndex], 0) in ['ACTION_SEND', 'ACTION_GET_CONTENT', 
												   		   					 '"android.intent.action.SEND"', '"android.intent.action.GET_CONTENT"']:
							# check if sink match
							if self.FlowDroid.getSinkMethod(self.sinks, self.sources[srcIndex][self.FlowDroid.FLOW]) == "createChooser":
								results, statFiles = self.FlowDroid.Bad2Good(results, statFiles, index, err, severity, self.verboseDeveloper)
								if len(results[index][1][severity]) == 0:
									statFiles[severity] -= 1
								break

					srcIndex += 1
			index += 1

		return results, statFiles

	def BadNotDetected(self, results, statFiles):
		results_cpy = copy.deepcopy(results)

		src_chooser = []
		src_without_chooser = []

		# We select only sources for which createChooser isn't a sink
		for src in self.sources:
			found = False
			for s in self.sinks:
				if src[self.FlowDroid.FLOW] == s[self.FlowDroid.ID]:
					if "<android.content.Intent: android.content.Intent createChooser(android.content.Intent,java.lang.CharSequence)>" in s[self.FlowDroid.INVOKE]:
						found = True
						break

			if not found:
				src_without_chooser.append(src)
			else:
				src_chooser.append(src)

		bad = []

		for w in src_without_chooser:
			mWithout = self.FlowDroid.getMethodSource(w)
			found = False
			for c in src_chooser:
				mWith = self.FlowDroid.getMethodSource(c)
				if mWith == mWithout:
					found = True
					break

			if not found:
				bad.append(w)

		bad_cpy = copy.deepcopy(bad)

		for b in bad_cpy:
			if (not (("<android.content.Intent: void <init>(java.lang.String)>" in b[self.FlowDroid.INVOKE] or
				"<android.content.Intent: android.content.Intent setAction(java.lang.String)>" in b[self.FlowDroid.INVOKE]) and
				self.FlowDroid.getArgInvoked(b, 0) in ['ACTION_SEND', 'ACTION_GET_CONTENT', '"android.intent.action.SEND"', '"android.intent.action.GET_CONTENT"'])):
				bad.remove(b)


		'''for e in self.sinks:
			print("-> ", e)

		for e in self.sources:
			print("* ", e)

		for e in bad:
			print("% ", e)'''

		# Search line code
		paths = Parser.getAllPath(self.apk.replace(".apk", "/"), 'java')

		for b in bad:
			p = self.FlowDroid.getPath(paths, b)
			m = self.FlowDroid.getMethodSource(b)
			keyword = self.getFctKeywordRule1(b)

			if p != None:
				fr = FileReader(p)
				line, tok = fr.getNextInstruction()
				while line != '':
					if tok[R.PATH] == m:
						if keyword in tok[R.INSTR]:
							results, statFiles = self.FlowDroid.appendBadToken(1, self.errMsg, tok, results, statFiles, p, R.CRITICAL)
							break


					line, tok = fr.getNextInstruction()
				fr.close()

		

		return results, statFiles





		