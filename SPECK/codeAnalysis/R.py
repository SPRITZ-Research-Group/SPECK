#!/usr/bin/python3

class R():
	# TOKEN STRUCTURE
	TYPE 		= "type"    # int
	VALUE 		= "value"   # string
	SCOPE 		= "scope"   # int
	PATH		= "path" 	# string

	ROOTID 		= "rootID"  # int
	BLOCKID 	= "blockID" # int
	CLASSID		= "clssID"  # int 	=> the numb of the class (it is one if it is the only, two if it is inside another class, ...)
	FUNCID		= "funcID"  # int 	=> it means that the function is the numb "funcID - 1" inside the class
	NBOBRACES	= "oBraces" # int 	=> numb of open braces before a certain name (var, class, method, ...)
	NBCBRACES	= "cBraces"	# int 	=> numb of closed braces before a certain name (var, class, method, ...)

	INTRY	    = "inTry"   # boolean 	=> is the instruction inside a try block?
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
	NA 			= "na"

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

		clss, fnc, path 	= R.getPath(className, funcName, package)
		token['funcName']	= fnc
		token['clssName']	= clss
		token[R.PATH]		= path

		return token


	@staticmethod
	def getPath(cName, fName, package):
		res = package
		className = cName.copy()		
		funcName = fName.copy()
		del className[0]
		del funcName[0]
		f = ""
		c = ""
		if len(className) > 0:
			res += "."
			c += className[0]
			for i in range(0, len(className)):
				res += className[i]
				# c += className[i]
				if i != len(className) - 1:
					res += "$"
					# c += "$"
		if len(funcName) > 0:
			res += "."
			f += funcName[0]
			for i in range(0, len(funcName)):
				res += funcName[i]
				# f += funcName[i]
				if i != len(funcName) - 1:
					res += "."
					# f += "."
		return c, f, res.replace("\n", "").strip()


