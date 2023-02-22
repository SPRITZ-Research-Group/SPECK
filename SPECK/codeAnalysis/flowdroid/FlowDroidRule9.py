#!/usr/bin/python3
import subprocess, os.path, copy, sys
from FlowDroid import *

class FlowDroidRule9():

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

	def getSinkById(self, Id):
		for s in self.sinks:
			if s[self.FlowDroid.ID] == Id:
				return s

	def GoodButBad(self, results, statFiles):
		'''print("=====")
		for e in self.sinks:
			print("-> ", e)

		for e in self.sources:
			print("* ", e)'''

		res = []
		# get flow from setdata to addflags
		for s in self.sources:
			for cursor in self.sources:
				if s[self.FlowDroid.FLOW] != cursor[self.FlowDroid.FLOW]:
					if (s[self.FlowDroid.INVOKE] == cursor [self.FlowDroid.INVOKE] and
						s[self.FlowDroid.METHOD] == cursor [self.FlowDroid.METHOD]):

						s1 = self.getSinkById(s[self.FlowDroid.FLOW])
						s2 = self.getSinkById(cursor[self.FlowDroid.FLOW])
						print(s)
						print("---")
						print(cursor)
						print("---")
						print(s1)
						print("---")
						print(s2)
						if "setData(android.net.Uri)>" in s1[self.FlowDroid.INVOKE]:
							if s1 not in res:
								res.append(s1)
						elif "setData(android.net.Uri)>" in s2[self.FlowDroid.INVOKE]:
							if s2 not in res:
								res.append(s2)
		
		'''for e in res:
			print("% ", e)'''
		
		return self.FlowDroid.GoodButBad(results, statFiles, res, self.verboseDeveloper)

	def BadNotDetected(self, results, statFiles):
		return results, statFiles





		