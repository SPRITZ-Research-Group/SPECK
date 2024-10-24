#!/usr/bin/python3

import sys

from FileReader import *
from Parser import *
from R import *
from XmlReader import *

from Rules import *

"""
RULE N°14

+ Check validity of data
** make sure that the contents of the data haven't been corrupted or modified
-> https://developer.android.com/topic/security/best-practices#external-storage
"""


class Rule13(Rules):
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
    ):
        Rules.__init__(
            self,
            directory,
            database,
            verbose,
            verboseDeveloper,
            storeManager,
            flowdroid,
            platform,
            validation,
            quiet,
        )

        self.AndroidErrMsg = "reading on external storage might not be checked"
        self.AndroidOkMsg = "reading on external storage (are) checked"
        self.AndroidText = "https://developer.android.com/topic/security/best-practices#external-storage"

        self.okMsg = "Data is checked when reading on external storage"
        self.errMsg = "Don't forget to double check the integrity of the data acquired from the external storage"
        self.category = R.CAT_4

        self.findXml()
        self.show(14, "Check validity of data")

    def checkReadOnExternalStorage(self, xmlReader, permissions):
        for p in permissions:
            for arg in p[XmlReader.ARGS]:
                if "android:name=" in arg:
                    value = xmlReader.getArgValue(arg)
                    if (
                        "READ_EXTERNAL_STORAGE" in value
                        or "WRITE_EXTERNAL_STORAGE" in value
                    ):
                        return True
        return False

    def checkInScope(self, inStream, validator):
        In = []
        NotIn = []

        inStream = Parser.setScopes(inStream)
        for elem in inStream:
            isIn = False

            for v in validator:
                if (
                    (elem[R.SCOPE] == R.VARGLOBAL)
                    or (
                        elem[R.SCOPE] == R.VARCLASS
                        and elem[R.CLASSID] == v[R.CLASSID]
                    )
                    or (
                        elem[R.SCOPE] == R.VARLOCAL
                        and elem[R.CLASSID] == v[R.CLASSID]
                        and elem[R.FUNCID] == v[R.FUNCID]
                    )
                ):

                    isIn = True
            if isIn == False:
                NotIn.append(elem)
            else:
                In.append(elem)

        return In, NotIn

    def run(self):
        self.loading()

        if self.manifest != None:
            xmlReader = XmlReader(self.manifest)

            # Check if READ_EXTERNAL_STORAGE is in manifest file
            permissions = xmlReader.getArgsTag("uses-permission")
            readOnExternalStorage = self.checkReadOnExternalStorage(
                xmlReader, permissions
            )

            if readOnExternalStorage:
                filt = Filter(
                    self.directory,
                    ["android.content.Context", "android.os.Environment"],
                )
                javaFiles = filt.execute()

                if len(javaFiles) > 0:
                    self.maxFiles = len(javaFiles)
                else:
                    self.loading()
                    self.updateN()

                for f in javaFiles:
                    fileReader = FileReader(f)

                    found = Parser.finder(
                        fileReader,
                        [
                            [
                                Parser.findLine,
                                ([["getExternalFilesDir("]], None),
                            ],
                            [
                                Parser.findLine,
                                ([["getExternalStorageDirectory("]], None),
                            ],
                            [
                                Parser.findLine,
                                (
                                    [["getExternalStoragePublicDirectory("]],
                                    None,
                                ),
                            ],
                            [
                                Parser.findLine,
                                ([["getExternalCacheDir("]], None),
                            ],
                            [
                                Parser.findLine,
                                ([["getExternalCacheDirs("]], None),
                            ],
                            [
                                Parser.findLine,
                                ([["getExternalFilesDir("]], None),
                            ],
                            [
                                Parser.findLine,
                                ([["getExternalFilesDirs("]], None),
                            ],
                            [
                                Parser.findLine,
                                ([["getExternalMediaDirs("]], None),
                            ],
                            # validator
                            [
                                Parser.findLine,
                                ([["new FileInputStream("]], None),
                            ],
                            [Parser.findLine, ([["openFileInput("]], None)],
                        ],
                    )

                    # Get all the lines where the external storage is required, then check for FileInputStream variables in that scope
                    inStream = (
                        found[0]
                        + found[1]
                        + found[2]
                        + found[3]
                        + found[4]
                        + found[5]
                        + found[6]
                        + found[7]
                    )
                    validator = found[8] + found[9]

                    # Check if each FileInputStream have a function which check validity of data in its scope
                    # sime: changed the order, since we check if the file is used as input and not if a validation function is called
                    NotIn, In = self.checkInScope(inStream, validator)

                    # Set log msg
                    In = Parser.setMsg(In, R.OK)
                    NotIn = Parser.setMsg(NotIn, R.WARNING, self.errMsg)

                    self.updateOWN(
                        f, In, NotIn, (len(NotIn) == 0 and len(In) == 0)
                    )
                    self.loading()
                    fileReader.close()

            else:
                self.loading()
                self.updateN()

            xmlReader.close()

        self.store(
            14,
            self.AndroidOkMsg,
            self.AndroidErrMsg,
            self.AndroidText,
            self.category,
        )
        self.display(FileReader)
