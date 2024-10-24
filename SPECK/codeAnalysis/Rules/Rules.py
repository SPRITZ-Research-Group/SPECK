#!/usr/bin/python3

import sys
from Filter import *
from Display import *
from StoreJson import *
from Storage import *
from XmlReader import *
from FlowDroid import *


def new_data():
    data = {}
    data[R.CRITICAL] = []
    data[R.WARNING] = []
    data[R.NA] = []
    data[R.OK] = []
    data[R.NOTHING] = []
    return data


flowdroid_err = [False]
flowdroid_enabled = [True]


def flowdroid_error():
    global flowdroid_err
    global flowdroid_enabled
    if not flowdroid_err[0]:
        flowdroid_err[0] = True


class Rules:
    def __init__(
        self,
        directory,
        database,
        verbose=True,
        verboseDeveloper=False,
        storeManager=None,
        flowdroid=False,
        platform="",
        validation=False,
        quiet=True,
        flowdroid_cb=True,
    ):
        self.directory = directory
        self.packageDir = self.getPackageName()
        self.database = database
        self.storeManager = storeManager
        self.verboseDeveloper = verboseDeveloper
        self.verbose = verbose
        self.quiet = quiet
        self.flowdroid = flowdroid
        self.flowdroid_cb = flowdroid_cb
        self.platform = platform
        self.validation = validation
        self.maxFiles = 0
        self.currentFileNb = 0
        self.results = []
        self.statFiles = Parser.initStatFiles()
        self.nb = 0

    def getPackageName(self):
        self.findXml(False)
        if self.manifest != None:
            try:
                xmlReader = XmlReader(self.manifest)
                manifest = xmlReader.getArgsTag("manifest")

                for arg in manifest[0][XmlReader.ARGS]:
                    if "package" in arg:
                        return xmlReader.getArgValue(arg).replace(".", "/")
            except:
                with open(self.manifest, "r") as f:
                    for l in f:
                        if "package=" in l:
                            s = l.find('package="') + len("package=") + 1
                            e = l[s:].find('"')
                            p = l[s : s + e]
                            return p
        return None

    @staticmethod
    def extractPkgNames(package):
        pkgList = []
        split = package.split(".")
        pkg1 = split[0]
        pkg2 = split[0] + ".*"
        for i in range(1, len(split)):
            pkgList.append(pkg1)
            pkgList.append(pkg2)
            pkg1 = pkg1 + "." + split[i]
            pkg2 = pkg2[0 : len(pkg2) - 2] + "." + split[i] + ".*"
        pkgList.append(pkg1)
        return pkgList

    # filter out all the java files based on the interesting package
    def filter(self, package, notFilt=False):
        if notFilt:
            self.javaFiles = Parser.getAllPath(self.directory, ".java")
            self.maxFiles = len(self.javaFiles)
        else:
            if type(package) == list:
                rules = []
                for p in package:
                    rules += Rules.extractPkgNames(p)
                filt = Filter(self.directory, rules)
            else:
                filt = Filter(self.directory, Rules.extractPkgNames(package))
            self.javaFiles = (
                filt.execute()
            )  # "filter" all the files, getting only the ones importing the "interesting package"
            self.maxFiles = len(self.javaFiles)

    # avoid adding the same files more than once
    def delDoublon(self, toadd):
        res = []
        for add in toadd:
            if not (add in self.javaFiles):
                res += [add]
        return res

    # same as filter, but with multiple "interesting" packages
    def filters(self, pkgs):
        self.javaFiles = []
        for pkg in pkgs:
            filt = Filter(self.directory, Rules.extractPkgNames(pkg))
            self.javaFiles += self.delDoublon(filt.execute())
        self.maxFiles = len(self.javaFiles)

    def findXml(self, incr=True):
        xmlFiles = Parser.getAllPath(self.directory, ".xml")
        for f in xmlFiles:
            if (
                "/build/intermediates/merged_manifest/debug/AndroidManifest.xml"
                in f
                or "/resources/AndroidManifest.xml" in f
            ):
                if incr:
                    self.maxFiles = 1
                self.manifest = f
                return
        if incr:
            self.maxFiles = 0
        self.manifest = None
        return

    # FIXED FOR NON-NUMBERED RULES
    def show(self, nb=0, title=""):
        if self.verbose:
            if isinstance(nb, int):
                self.nb = nb
                print(
                    f"\n\033[96m\033[01m[§] RULE: {nb}\033[0m\033[0m\n\033[37m[=>] {title}\033[0m"
                )
            else:
                print(f"\n\033[96m\033[01m[§] RULE: {nb}\033[0m\033[0m")

    def loading(self, isLast=False):
        if self.verbose:  # and not self.quiet:
            sys.stdout.flush()
            string = f"\033[37m[=>] \033[01m{self.currentFileNb}/{self.maxFiles}\033[0m file(s) analysed\033[0m"
            if self.currentFileNb == self.maxFiles or isLast:
                print(f"{string}\n")
            else:
                print(f"{string}", end="\r")
            self.currentFileNb += 1

    # Id is the rule number
    # Most parameter are not needed
    def store(
        self,
        Id=-1,
        AndroidOkMsg="",
        AndroidErrMsg="",
        AndroidText="",
        category=R.CAT_NA,
        withBol=False,
        err=[],
    ):
        # FLOWDROID
        if self.flowdroid and flowdroid_enabled[0] and self.platform != "":
            if self.verbose:
                print("\033[36m[?] FlowDroid option detected\033[0m")
            apk = self.directory
            if self.directory.endswith("/"):
                apk = apk[:-1]
            apk = f"{apk}.apk"
            if not os.path.isfile(apk):
                # print("looking for apk...")
                apks = Parser.getAllPath(self.directory, ".apk")
                # print(apks)
                if len(apks) > 0:
                    apk = apks[0]
            fdroid = FlowDroid(
                Id,
                apk,
                self.platform,
                self.verbose,
                self.verboseDeveloper,
                err,
                cb=not (self.flowdroid_cb and flowdroid_err[0]),
            )
            self.results, self.statFiles = fdroid.run(
                self.results, self.statFiles
            )

        # STOREMANAGER
        if self.storeManager != None:
            apk = self.directory
            if self.directory.endswith("/"):
                apk = self.directory[:-1]
            StoreJson.showResults(
                self.results,
                None,
                XmlReader,
                self.packageDir,
                None,
                Id,
                apk,
                self.database,
                AndroidErrMsg,
            )

    # just display the results
    def display(self, Reader=None):
        if self.verbose:
            if self.quiet:
                apk = self.directory
                if self.directory.endswith("/"):
                    apk = self.directory[:-1]
                StoreJson.showResults(
                    self.results,
                    self.statFiles,
                    Reader,
                    self.packageDir,
                    self.validation,
                    self.nb,
                    apk,
                    mongo_cfg=self.database,
                )
            else:
                Display.showResults(
                    self.results,
                    self.statFiles,
                    Reader,
                    self.packageDir,
                    self.validation,
                    self.nb,
                )

    # OK CRITICAL NOTHING
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
        data = new_data()
        data[R.CRITICAL] = NotIn
        if not self.verboseDeveloper:
            data[R.OK] = In
        self.results.append([filename, data])

    # OK WARNING NOTHING
    def updateOWN(self, filename, In, NotIn, NothingCond):
        if not self.verboseDeveloper:
            if len(NotIn) > 0:
                self.statFiles[R.WARNING] += 1
            if len(In) > 0:
                self.statFiles[R.OK] += 1
            if NothingCond:
                self.statFiles[R.NOTHING] += 1
        else:
            if len(NotIn) > 0:
                self.statFiles[R.WARNING] += 1
            else:
                self.statFiles[R.NOTHING] += 1
        data = new_data()
        data[R.WARNING] = NotIn
        if not self.verboseDeveloper:
            data[R.OK] = In
        self.results.append([filename, data])

    # CRITICAL NOTHING
    def updateCN(self, filename, NotIn):
        if len(NotIn) > 0:
            self.statFiles[R.CRITICAL] += 1
        else:
            self.statFiles[R.NOTHING] += 1
        data = new_data()
        data[R.CRITICAL] = NotIn
        self.results.append([filename, data])

    # WARNING NOTHING
    def updateWN(self, filename, NotIn):
        if len(NotIn) > 0:
            self.statFiles[R.WARNING] += 1
        else:
            self.statFiles[R.NOTHING] += 1
        data = new_data()
        data[R.WARNING] = NotIn
        self.results.append([filename, data])

    # OK NOTHING
    def updateON(self, filename, In):
        data = new_data()
        if not self.verboseDeveloper:
            self.statFiles[R.OK] += 1
            data[R.OK] = In
        else:
            self.statFiles[R.NOTHING] += 1
        self.results.append([filename, data])

    # CRITICAL
    def updateC(self, msg, NotIn):
        self.statFiles[R.CRITICAL] += 1
        data = new_data()
        data[R.CRITICAL] = NotIn
        self.results.append([msg, data])

    # NOTHING
    def updateN(self):
        self.statFiles[R.NOTHING] += 1

    # Custom --> used by the interpreter
    # Not really needed for the interpreter --> just for showing
    def just_update(self, filename, NotIn):
        severities = ["ok", "warning", "critical", "na"]
        try:
            severity = NotIn[0][
                "eType"
            ]  # because NotIn is a list of dicts (very often of one dict)
        except Exception as e:
            severity = R.NA
        if severity not in severities:
            severity = R.NA
        if len(NotIn) > 0:
            self.statFiles[severity] += 1
        # Needed
        data = new_data()
        data[severity] = NotIn
        self.results.append(
            [filename, data]
        )  # maybe I have to insert this part also in the prev funct (e.g. updateC, updateON, ...)
