#!/usr/bin/python3

class R():
	# TOKEN STRUCTURE
	TYPE 		= "type"    # int
	VALUE 		= "value"   # string
	SCOPE 		= "scope"   # int
	PATH		= "path" 	# string

	ROOTID 		= "rootID"  # int
	BLOCKID 	= "blockID" # int
	CLASSID		= "clssID"  # int
	FUNCID		= "funcID"  # int
	NBOBRACES	= "oBraces" # int
	NBCBRACES	= "cBraces"	# int

	INTRY	    = "inTry"   # boolean
	INSTR	    = "instr"   # string
	EXTRA		= "extra"	# string

	# -> TYPE
	VARNAME 	= 1
	TYPEVAR 	= 2
	OBJNAME  	= 3
	ARGNAME 	= 4

	CLASS 		= 5
	FUNC 		= 6

	# -> SCOPE
	VARGLOBAL   = 1
	VARCLASS    = 2
	VARLOCAL	= 3

	# DISPLAY RESULTS
	ERRORTYPE	= "eType"
	ERRORMSG	= "eMsg"

	# -> ERRORTYPE
	OK			= "ok"
	WARNING		= "warning"
	CRITICAL	= "critical"
	NOTHING		= "none"

	# CATEGORY
	CAT_1		= "Interprocess communication"
	CAT_2		= "Networking"
	CAT_3		= "Permissions"
	CAT_4		= "Data"
	CAT_5		= "Cryptography"
	CAT_NA		= "Other"

	@staticmethod
	def constructToken(rootID, blockID, classID, funcID, nbOBraces, nbCBraces, inTry, line, className, funcName, package):
		token = {}
		token[R.TYPE] 		= None
		token[R.VALUE] 		= None
		token[R.SCOPE] 		= None

		token[R.ERRORTYPE] 	= None
		token[R.ERRORMSG]	= None

		token[R.ROOTID] 	= rootID
		token[R.BLOCKID] 	= blockID
		token[R.CLASSID] 	= classID
		token[R.FUNCID] 	= funcID

		token[R.NBOBRACES]	= nbOBraces
		token[R.NBCBRACES]	= nbCBraces

		token[R.INTRY] 		= inTry
		token[R.INSTR] 		= line

		token[R.PATH]		= R.getPath(className, funcName, package)

		return token

	@staticmethod
	def getPath(cName, fName, package):
		res = package

		className = cName.copy()
		funcName = fName.copy()
		del className[0]
		del funcName[0]

		if len(className) > 0:
			res += "."

			for i in range(0, len(className)):
				res += className[i]
				if i != len(className) - 1:
					res += "$"

		if len(funcName) > 0:
			res += "."

			for i in range(0, len(funcName)):
				res += funcName[i]
				if i != len(funcName) - 1:
					res += "."

		return res.replace("\n", "").strip()






