#!/usr/bin/python3

from Rules import *
from FileReader import *
from Parser import *
from R import *
from Common import *
import sys


"""
RULE N°17

+ Avoid SQL injection
-> https://developer.android.com/training/articles/security-tips#ContentProviders

? Pseudo Code:
	1. Look for classes which extend ‘ContentProvider’
	2. Check method names (whitelist: query, update, delete)

! Output
	-> NOTHING	: no class which extends 'ContentProvider' found
	-> OK 		: class which extends 'ContentProvider' use only whitelisted methods
	-> CRITICAL	: class which extends 'ContentProvider' doesn't use only whitelisted methods
"""


class Rule16(Rules):
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

        self.AndroidErrMsg = (
            "content provider(s) might be subject to SQL injection"
        )
        self.AndroidOkMsg = (
            "content provider(s) (are) not subject to SQL injection"
        )
        self.AndroidText = "https://developer.android.com/training/articles/security-tips#ContentProviders"

        self.okMsg = "Content provider use only whitelisted methods"
        self.errMsg = "Content provider doesn't use only whitelisted methods (query, update and delete)"
        self.category = R.CAT_2

        self.filter("android.content.ContentProvider")
        self.show(17, "Avoid SQL injection")

    def check(self, listClss, listFunc):
        In = []
        NotIn = []

        blackList = ["query(", "query ("]  # CORRECT -> UNCOMMENT!
        for clss in listClss:
            if (
                "extends" in clss[R.INSTR]
                and "ContentProvider" in clss[R.INSTR]
            ):
                isOk = True
                for func in listFunc:
                    if func[R.CLASSID] == clss[R.CLASSID]:
                        if any(elem in func[R.INSTR] for elem in blackList):
                            NotIn.append(func)
                            isOk = False

                if isOk:
                    In.append(clss)

        return In, NotIn

    def run(self):
        self.loading()

        for f in self.javaFiles:
            fileReader = FileReader(f)

            listClss, listFunc = Common.get_classes_and_funcs(fileReader)
            extendsContentProvider = Common.get_extends_class(
                listClss, "ContentProvider"
            )

            In = []
            NotIn = []
            blackList = ["query(", "query ("]
            for extends in extendsContentProvider:
                isOk = True
                for func in listFunc:
                    if func[R.CLASSID] == extends[R.CLASSID]:
                        if Common.match_any_in_list(func[R.INSTR], blackList):
                            NotIn.append(func)
                            isOk = False

                if isOk:
                    In.append(extends)

            # Set log msg
            In = Parser.setMsg(In, R.OK)
            NotIn = Parser.setMsg(NotIn, R.CRITICAL, self.errMsg)

            self.updateOCN(f, In, NotIn, (len(In) == 0 and len(NotIn) == 0))
            self.loading()
            fileReader.close()

        self.store(
            17,
            self.AndroidOkMsg,
            self.AndroidErrMsg,
            self.AndroidText,
            self.category,
        )
        self.display(FileReader)
