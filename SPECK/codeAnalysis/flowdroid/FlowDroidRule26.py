#!/usr/bin/python3
import copy
import os.path
import subprocess
import sys
from R import *
from Parser import *
from FlowDroid import *


class FlowDroidRule26:
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
        """print("26 =====")
        for e in self.sinks:
                print("-> ", e)

        for e in self.sources:
                print("* ", e)"""

        sckt = []
        sessions = []
        for s in self.sources:
            if "createSocket" in s[self.FlowDroid.INVOKE]:
                sckt.append(s)
            else:
                sessions.append(s)

        good = []
        todel = []
        tokens = []

        for elem in sckt:
            sink = self.FlowDroid.getSinkById(elem[self.FlowDroid.FLOW], self.sinks)
            path = self.FlowDroid.getMethodSource(sink)

            for sess in sessions:
                if path == self.FlowDroid.getMethodSource(sess):
                    good.append(elem)
                    todel.append(sess)
                    break

        paths = Parser.getAllPath(self.apk.replace(".apk", "/"), "java")
        for d in todel:
            p = self.FlowDroid.getPath(paths, d)
            m = self.FlowDroid.getMethodSource(d)

            if p != None:
                fr = FileReader(p)
                line, tok = fr.getNextInstruction()
                while line != "":
                    if tok[R.PATH] == m:
                        tokens.append(tok)
                        break

                    line, tok = fr.getNextInstruction()
                fr.close()

        results, statFiles = self.FlowDroid.delete(results, statFiles, tokens, R.OK)

        return self.FlowDroid.GoodButBad(
            results, statFiles, good, self.verboseDeveloper
        )

    def BadNotDetected(self, results, statFiles):
        return results, statFiles
