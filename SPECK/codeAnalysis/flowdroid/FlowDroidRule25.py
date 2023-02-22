#!/usr/bin/python3
import copy
import os.path
import subprocess
import sys
from R import *
from FlowDroid import *


class FlowDroidRule25:
    def __init__(self, flowDroid, apk, sources, sinks, errMsg, verboseDeveloper):
        self.FlowDroid = flowDroid
        self.sources = sources
        self.sinks = sinks
        self.errMsg = errMsg
        self.verboseDeveloper = verboseDeveloper
        self.apk = apk

    def start(self, results, statFiles):
        results, statFiles = self.BadButGood(results, statFiles)
        results, statFiles = self.BadNotDetected(results, statFiles)
        return results, statFiles

    def BadButGood(self, results, statFiles):
        """print("27 =====")
        for e in self.sinks:
                print("-> ", e)

        for e in self.sources:
                print("* ", e)"""

        return self.FlowDroid.BadButGood(
            results, statFiles, self.sources, self.verboseDeveloper, R.CRITICAL
        )

    def BadNotDetected(self, results, statFiles):
        return results, statFiles
