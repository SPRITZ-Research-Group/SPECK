#!/usr/bin/python3

import sys
from Filter import *
from Display import *
from StoreJson import *
from Storage import *
from Parser import *
from R import *
from XmlReader import *
from FlowDroid import *

class Rules():
    def __init__(self, directory, database, verbose=True, verboseDeveloper=False, storeManager=None, flowdroid=False, platform="" , validation=False, quiet=True):
        self.directory = directory
        self.packageDir = self.getPackageName()

        self.database=database

        self.storeManager = storeManager
        self.verboseDeveloper = verboseDeveloper
        self.verbose = verbose
        self.quiet = quiet

        self.flowdroid = flowdroid
        self.platform = platform

        self.validation = validation

        self.maxFiles = 0
        self.currentFileNb = 0

        self.results = []
        self.statFiles = Parser.initStatFiles()

        self.nb=0

    def getPackageName(self):
        self.findXml(False)
        if self.manifest != None:
            try:
                xmlReader = XmlReader(self.manifest)
                manifest = xmlReader.getArgsTag("manifest")

                for arg in manifest[0][XmlReader.ARGS]:
                    if 'package' in arg:
                        return xmlReader.getArgValue(arg).replace(".", "/")
            except:
                with open(self.manifest, 'r') as f:
                    for l in f:
                        if "package=" in l:
                            s = l.find("package=\"") + len("package=") + 1
                            e = l[s:].find("\"")
                            p = l[s:s+e]
                            return p

        return None

    @staticmethod
    def extractPkgNames(package):
        pkgList = []

        split = package.split('.')

        pkg1 = split[0]
        pkg2 = split[0]+".*"
        for i in range(1, len(split)):
            pkgList.append(pkg1)
            pkgList.append(pkg2)
            pkg1 = pkg1+"."+split[i]
            pkg2 = pkg2[0:len(pkg2)-2]+"."+split[i]+".*"

        pkgList.append(pkg1)
        return pkgList

    def filter(self, package, notFilt=False):
        if notFilt:
            self.javaFiles = Parser.getAllPath(self.directory, '.java')
            self.maxFiles = len(self.javaFiles)
        else:
            filt = Filter(self.directory, Rules.extractPkgNames(package))
            self.javaFiles = filt.execute()
            self.maxFiles = len(self.javaFiles)

    def delDoublon(self, toadd):
        res = []
        for add in toadd:
            if not (add in self.javaFiles):
                res += [add]
        return res

    def filters(self, pkgs):
        self.javaFiles = []
        for pkg in pkgs:
            filt = Filter(self.directory, Rules.extractPkgNames(pkg))
            self.javaFiles += self.delDoublon(filt.execute())
        self.maxFiles = len(self.javaFiles)

    def findXml(self, incr=True):
        xmlFiles = Parser.getAllPath(self.directory, '.xml')
        for f in xmlFiles:
            if "AndroidManifest.xml" in f:
                if incr:
                    self.maxFiles = 1
                self.manifest = f
                return
        if incr:
            self.maxFiles = 0
        self.manifest = None
        return

    def show(self, nb, title):
        if self.verbose:
            self.nb=nb
            print("\n\033[96m\033[01m[#] RULE {}\033[0m\033[0m\n\033[37m[=>] {}\033[0m".format(nb, title))

    def loading(self, isLast=False):
        if self.verbose: # and not self.quiet:
            sys.stdout.flush()
            string = "\033[37m[=>] \033[01m{}/{}\033[0m file(s) analysed\033[0m".format(self.currentFileNb, self.maxFiles)
            if (self.currentFileNb == self.maxFiles or isLast):
                print("{}\n".format(string))
            else:
                print("{}".format(string), end="\r")
            self.currentFileNb += 1

    def store(self, Id, AndroidOkMsg, AndroidErrMsg, AndroidText, category, withBol=False, err=[]):
        # FLOWDROID
        if self.flowdroid and self.platform != "":
            if self.verbose:
                print("\033[36m[?] FlowDroid option detected\033[0m")

            apk = self.directory
            if self.directory.endswith("/"):
                apk = self.directory[:-1]

            fdroid = FlowDroid(Id, apk + ".apk", self.platform, self.verbose, self.verboseDeveloper, err)
            self.results, self.statFiles = fdroid.run(self.results, self.statFiles)

        # STOREMANAGER
        if self.storeManager != None:
            # print(self.results)
            apk = self.directory
            if self.directory.endswith("/"):
                apk = self.directory[:-1]

            StoreJson.showResults(self.results, None, XmlReader, self.packageDir, None, Id, apk, self.database, AndroidErrMsg)
            

    def display(self, Reader):
        if self.verbose:
            if self.quiet:
                apk = self.directory
                if self.directory.endswith("/"):
                    apk = self.directory[:-1]
                StoreJson.showResults(self.results, self.statFiles, Reader, self.packageDir, self.validation, self.nb, apk, self.database)
            else:
                Display.showResults(self.results, self.statFiles, Reader, self.packageDir, self.validation, self.nb)

    def updateOCN(self, filename, In, NotIn, NothingCond):
        if not self.verboseDeveloper:
            if len(NotIn) > 0:
                self.statFiles[R.CRITICAL] += 1
            if len(In) > 0:
                self.statFiles[R.OK] += 1
            if NothingCond:
                self.statFiles[R.NOTHING] += 1
        else:
            if len(NotIn) > 0:
                self.statFiles[R.CRITICAL] += 1
            else:
                self.statFiles[R.NOTHING] += 1

        data = {}
        data[R.CRITICAL] = NotIn
        if not self.verboseDeveloper:
            data[R.OK]  = In

        self.results.append([ filename, data ])

    def updateOWN(self, filename, In, NotIn, NothingCond):
        if not self.verboseDeveloper:
            if len(NotIn) > 0:
                self.statFiles[R.WARNING] += 1
            if (len(In) > 0):
                self.statFiles[R.OK] += 1
            if NothingCond:
                self.statFiles[R.NOTHING] += 1
        else:
            if len(NotIn) > 0:
                self.statFiles[R.WARNING] += 1
            else:
                self.statFiles[R.NOTHING] += 1

        data = {}
        data[R.WARNING] = NotIn
        if not self.verboseDeveloper:
            data[R.OK] = In

        self.results.append([ filename, data ])

    def updateCN(self, filename, NotIn):
        if len(NotIn) > 0:
            self.statFiles[R.CRITICAL] += 1
        else:
            self.statFiles[R.NOTHING] += 1

        data = {}
        data[R.CRITICAL] = NotIn

        self.results.append([ filename, data ])

    def updateWN(self, filename, NotIn):
        if len(NotIn) > 0:
            self.statFiles[R.WARNING] += 1
        else:
            self.statFiles[R.NOTHING] += 1

        data = {}
        data[R.WARNING] = NotIn

        self.results.append([ filename, data ])

    def updateON(self, filename, In):
        data = {}
        if not self.verboseDeveloper:
            self.statFiles[R.OK] += 1
            data[R.OK] = In
        else:
            self.statFiles[R.NOTHING] += 1

        self.results.append([ filename, data ])

    def updateC(self, msg, NotIn):
        self.statFiles[R.CRITICAL] += 1
        data = {}
        data[R.CRITICAL] = NotIn

        self.results.append([msg, data])

    def updateN(self):
        self.statFiles[R.NOTHING] += 1
