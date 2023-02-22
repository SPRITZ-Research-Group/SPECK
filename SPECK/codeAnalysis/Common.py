#!/usr/bin/python3
from copy import copy as cpy
import re

# Internals
from Rules import *
from FileReader import *
from Parser import *
from Filter import *
from R import *

from CommonPlumbing import *

####################################################################################################
#                                    Common Behaviours of Rules                                    #
####################################################################################################

class Common():

	####################################################################################################
	#                                   getAll + checkCallAndGetArg                                    #
	####################################################################################################

	########################################
	#                getAll                #
	########################################
	# Get all occurrences of a specified method/variable associated to a specific call.
	# Consider using a list a list of conditions -> for performance reasons (but maybe not that much!)

	# findVarName: returns the variable name present in the line that respects all the conditions
	@staticmethod
	def get_all_var_names(fileReader, conditions): 
		# conditions must be an array of strings and its length > 0
		return Parser.finder(fileReader, [[Parser.findVarName, (conditions, None)]])[0] # [0] because only one condition list passed


	# findTypeVar: returns the type of the variable
	@staticmethod
	def get_all_var_types(fileReader, conditions):
		# conditions must be an array of strings and its length > 0
		return Parser.finder(fileReader, [[Parser.findTypeVar, (conditions, None)]])[0]


	# findObjName: returns the name of the object which calls the specified method
	@staticmethod
	def get_all_obj_names(fileReader, method):
		return Parser.finder(fileReader, [[Parser.findObjName, (method, None)]])[0]


	# findArgName: first argument is the method name, the second is the argument of that method that we want
	@staticmethod
	def get_all_arg_names(fileReader, method, arg_position):
		# method is the method we want to check is called
		# arg_position is the position of the arg we are interested into
		return Parser.finder(fileReader, [[Parser.findArgName, (method, arg_position, None)]])[0]


	# It retrieves all args names (not only one as the prev method)
	# findArgName: first argument is the method name, the second is the argument of that method that we want
	@staticmethod
	def get_all_args_names(fileReader, method, arg_positions):
		# method is the method we want to check is called
		# arg_positions is a list with the positions of the args we are interested into
		return Parser.finder(fileReader, [[Parser.findArgsName, (method, arg_positions, None)]])[0]


	########################################
	#          checkCallAndGetArg          #
	########################################

	# search in the code if a method/function is called and check its arguments
	# whitelist is an array containing all the possible good values for the argument
	@staticmethod
	def check_call_and_arg(fileReader, method, arg_position, whitelist):
		found = Common.get_all_arg_names(fileReader, method, arg_position)
		In = []
		NotIn = []
		for f in found:
			if f[R.VALUE] in whitelist: 	# can also use Common.match_any_in_list(f[R.VALUE], whitelist)
				In.append(f)
			else:
				NotIn.append(f)
		return found, In, NotIn


	# returns all class and function definitions
	@staticmethod
	def get_classes_and_funcs(fileReader):
		return Parser.getClassNFunc(fileReader)


	# find all those classes that extends a specific class
	@staticmethod
	def get_extends_class(classes_list, extended_class):
		output = []
		for clss in classes_list:
			instr = clss[R.INSTR]
			if ' extends ' in instr:
				splitted_instr = instr.split(' extends ')[1].strip() 	# consider only the right part
				if extended_class == splitted_instr: 	# splitting ' extends ', it is not needed to use 'in': there must be a complete match
					output.append(clss)
		return output


	# find all those classes that implements a specific interface
	@staticmethod
	def get_implements_class(classes_list, implemented_interface):
		output = []
		for clss in classes_list:
			instr = clss[R.INSTR]
			if ' implements ' in instr:
				splitted_instr = instr.split(' implements ')[1].strip() 	# consider only the right part
				if implemented_interface == splitted_instr: 	# splitting ' implements ', it is not needed to use 'in': there must be a complete match
					output.append(clss)
		return output


	########################################
	#               Compare                #
	########################################
	# Compare the content of 2 arrays/lists (used after getAll for instance).
	# BE CAREFUL ! reference must have 'SCOPE' field initialized.

	# scopeType is used to choose one of the 3 scope functions; in the case a scope different from
	# NORMAL_SCOPE is used, then a scopeAssistant array should be specified
	# There are 2 scopeTypes and 2 scopeAssistants, one for each array (in the same order)
	# Questions:
	# - reverse ?
	@staticmethod
	def compare(arr1, arr2, reverse=False, with1=False, scope_with1=[], with2=False, scope_with2=[]):

		########################################
		#              Set scopes              #
		########################################

		if with1:
			if len(scope_with1) > 0 and scope_with1[0]['scope'] == None:
				scope_with1 = Parser.setScopes(scope_with1)
			arr1 = Parser.setScopesWith(arr1, scope_with1)
		else:
			arr1 = Parser.setScopes(arr1)

		if with2:
			if len(scope_with2) > 0 and scope_with2[0]['scope'] == None:
				scope_with2 = Parser.setScopes(scope_with2)
			arr2 = Parser.setScopesWith(arr2, scope_with2)
		else:
			arr2 = Parser.setScopes(arr2)

		return Parser.diff(arr1, arr2, reverse) # return In, NotIn


	########################################
	#             Analyze XML              #
	########################################
	# Used when XML is needed to be analysed (e.g. getting permissions,check if components are exported, ...)

	# This function returns all the arguments of all the occurences of the specified tag
	# It SHOULD return the 'arg="value"' pair
	@staticmethod
	def get_xml_tag_args(xmlReader, tag):
		return xmlReader.getArgsTag(tag)


	# It returns all the arguments of all the occurences of the specified tag under a specified condition
	@staticmethod
	def get_xml_tag_args_condition(xmlReader, tag, cond):
		return xmlReader.getArgsCond(tag, cond)


	# Return a list of the arguments (string object) of the child subelement with a specified attribute, which is under parent and (eventually) grandparent elements
	@staticmethod
	def get_xml_tag_args_child(xmlReader, child, attribute, parent, granparent=None):
		return xmlReader.getArgsChild(child, attribute, parent, granparent)


	# Return a list of the 'android:name' values of a given 'action' element which is under a specific component element (e.g. receiver, services, ...)
	@staticmethod
	def get_action_attr_names(xmlReader, component_el, component_attr_list, action_el):
		return xmlReader.getActionNames(component_el, component_attr_list, action_el)


	# This function returns the arg-value pair splitted
	@staticmethod
	def get_arg_value_split(arg):
		split = arg.split("=")
		argName = split[0].strip()
		val = split[1].strip()
		value = val[1:len(val)-1]
		return argName, value


	# Function used to check if a specific argument is present in a list: if that's the case, return its position in the list
	# It also returns the corresponding value
	@staticmethod
	def get_arg_index_and_value(args, arg):
		for i in range(len(args)):
			if arg in args[i]:
				_, value = Common.get_arg_value_split(args[i])
				return i, value 		# found at index i
		return -1, None 				# not found


	########################################
	#            searcKeywords             #
	########################################
	
	# Check if a keyword is present in the code
	# findLine: returns the occurrences of the found keywords
	@staticmethod
	def search_keywords(fileReader, keywords, withStrings=False, arrayOfArrays=False): 
		# keywords should be an array of arrays --> unless specified, accept an array of strings
		# withStrings allows us to search data between quotes
		# arrayOfArrays: is used in case we want some that some keywords occur together
		words = []
		if not arrayOfArrays:	# array of strings
			if isinstance(keywords, str):
				words.append([keywords])
			else:
				for k in keywords:
					words.append([k])
		else:
			words = keywords
		return Parser.finder(fileReader,[[Parser.findLine, (words, withStrings, None)]])[0]


	# Generalized from Rule1.getSetAction
	# This function is used to match the objects which call a specific method to a corresponding variable name,
	# using some (optional) conditions. First, the conditions are checked over the objects. Then, the scope of the 
	# objects passing the screening over the conditions is calculated, and finally if the scope in not None, it is returned
	# Arguments:
	# - variables: list of variables' names returned by get_all_var_names
	# - objects: list of objects' names returned by get_all_obj_names
	# - conditions: optional argument, specifying the conditions for selecting which objects to match with vars
	@staticmethod
	def match_obj_with_vars(variables, objects, conditions=[]):
		output = []
		if len(conditions) > 0:
			for o in objects:
				# if any(c in o[R.INSTR] for c in conditions):
				if Common.match_any_in_list(o[R.INSTR], conditions):
					output.append(o)
		variables = Parser.setScopes(variables)
		objects = Parser.setScopesWith(output, variables)
		output = []
		for o in objects:
			if o[R.SCOPE] != None:
				output.append(o)
		return output


	# Function used to check if any string in the str_list is present inside the string argument
	@staticmethod
	def match_any_in_list(string, str_list):
		return any(elem in string for elem in str_list)


	# Function that outputs the XmlReader obj corresponding to an xml file different from AndroidManifest (e.g. network_security_config.xml)
    # 'arg_value' should be the xml argument value
    # it works by replacing the AndroidManifest path with the 'arg_value' one
	@staticmethod
	def analyse_non_manifest_xml(manifest_path, arg_value):
		# case where we check our developed app
		if 'build/intermediates/merged_manifest' in manifest_path:
			xml_file_path = manifest_path.replace('build/intermediates/merged_manifest/debug/AndroidManifest.xml', 'src/main/res/') + arg_value.replace('@', '') + '.xml'
		# case where we check an app decompiled from apk
		else:
			xml_file_path = manifest_path.replace('AndroidManifest.xml', 'res/') + arg_value.replace('@', '') + '.xml'
		# self.maxFiles += 1 # this is used as a display thing... --> let the interpreter add it!
		return XmlReader(xml_file_path), xml_file_path

	# Function that outputs the path to an xml file different from AndroidManifest (e.g. network_security_config.xml)
    # 'arg_value' should be the xml argument value
    # it works by replacing the AndroidManifest path with the 'arg_value' one
	@staticmethod
	def get_non_manifest_xml_path(manifest_path, arg_value):
		# case where we check our developed app
		if 'build/intermediates/merged_manifest' in manifest_path:
			xml_file_path = manifest_path.replace('build/intermediates/merged_manifest/debug/AndroidManifest.xml', 'src/main/res/') + arg_value.replace('@', '') + '.xml'
		# case where we check an app decompiled from apk
		else:
			xml_file_path = manifest_path.replace('AndroidManifest.xml', 'res/') + arg_value.replace('@', '') + '.xml'
		# self.maxFiles += 1 # this is used as a display thing... --> let the interpreter add it!
		xml_file_path

	# Wrapper function to help the user set an error message for a specific violation
	@staticmethod
	def set_err_msg(arr, err_msg, severity=R.NA):
		return Parser.setMsg(arr, severity, err_msg)


	# Drawback of this function: if methods are concatenated, only the first one is chosen
	@staticmethod
	def get_func_args(func):
		# print(f'FUNC: {func}')
		splitted = func.split('(')[1].split(')')[0]
		args = splitted.split(', ')
		return args


	# @staticmethod
	# # SKIPPED
	# def get_file_and_block_info(fileReader, clssID, funcID):
	# 	# Get Class and Method in which the violation is detected
	# 	classes, funcs = Common.get_classes_and_funcs(fileReader)
	# 	clss = classes[clssID-1]	# -1 because id starts from 1
	# 	# func = funcs[funcID-2]		# -1 because id starts from 1 (2 why?)
	# 	func = funcs[funcID-1]		# -1 because id starts from 1 (2 why?)

	# 	# Get file package --> use to filter out java files
	# 	package = Common.search_keywords(fileReader, 'package')[0]
	# 	clss_name = clss['path'].split('.')[1].strip()
	# 	pkg_name = package['value'].split('package')[1].strip(' ;')
	# 	filter_package = pkg_name + "." + clss_name		# used to filter out java files

	# 	# Return the class token, the function token, and the package needed to filter out java files when searching from the interesting value
	# 	return clss, func, filter_package


	# returns the package name of the current file
	@staticmethod
	def get_file_pkg(fileReader, clss, func):
		# Get file package --> use to filter out java files
		package = Common.search_keywords(fileReader, 'package')[0]

		# Test
		classes, funcs = Common.get_classes_and_funcs(fileReader)
		ret_func = None

		for f in funcs:
			if func in f['instr']:
				ret_func = f 
				break
		pkg_name = package['value'].split('package')[1].strip(' ;')
		return  ret_func, pkg_name + "." + clss		# used to filter out java files


	# Search through a list if key is present and, if yes, return its position index inside the list
	@staticmethod
	def get_position_index(lst, key):
		for i in range(len(lst)):
			if key in lst[i]:
				return i 
		return -1


	@staticmethod
	def get_unique(lst):			# 'lst' is someting like [True, [value], True, [value], ...] 
		output = []
		for i in range(0, len(lst)-1, 2):	# check only even list value ...
			if lst[i] == True:				# ... if it is 'True' ...
				output += lst[i+1]			# ... then append the next value => it is a CONSTANT
		# return list(set(lst))
		return output

	
	########################################
	#             B. Variable              #
	########################################

	# Return the corresponding initialisations of the 'name' variable for the corresponding scope
	@staticmethod
	def check_scope(fileReader, name, funcId, instr):
		# [' '+name+" ="] is standard because we want the declaration of a variable with that name
		# FixMeLater: -> Try using also get_all_var_names --> it seems more efficient
		var_types = Common.get_all_var_types(fileReader, [' '+name+" ="])	# using '=' excludes smth like 'public name;'
		var_types = Parser.setScopes(var_types)	# set the scope
		current_func = []
		current_class = []
		global_scope = []
		names = []
		for var in var_types:
			# print(f'\n\nVAR\n{var}\nVAR\n\n')
			if var['funcID'] == funcId:
				current_func.append(extract_var_value(var['instr']))
			elif var['scope'] == R.VARCLASS:
				current_class.append(extract_var_value(var['instr']))
			elif var['scope'] == R.VARGLOBAL:
				global_scope.append(extract_var_value(var['instr']))		# FixMeLater: -> However, it could happen a re-initialisation: this.x = 'a' ...
		
		if len(current_func) > 0:
			names += current_func
		elif len(current_class) > 0:
			names += current_class
		elif len(global_scope) > 0:
			names += global_scope
		else:
			raise CustomError(f'No var {name} in scope\nINSTR:\t{instr}')

		return names


	########################################
	#            C. Method call            #
	########################################

	@staticmethod
	def is_method_call(name):
		return name.endswith(')') and '(' in name and '.' in name


	# @staticmethod
	# def get_method_args(name):
	# 	parentheses = 0
	# 	add_char = False
	# 	comma_list = ''
	# 	for char in name:
	# 		if parentheses > 0:
	# 			add_char = True

	# 		if char == '(':
	# 			parentheses += 1
	# 		elif char == ')':
	# 			parentheses -= 1

	# 		if parentheses > 0 and add_char:
	# 			comma_list += char

	# 		if parentheses == 0 and add_char:
	# 			break

	# 	args_list = comma_list.split(',')
	# 	return [arg.strip() for arg in args_list]


	########################################
	#            Python Closure            #
	########################################
	
	@staticmethod
	def chase_value_outer(file_reader, directory, var_name, token, allowed=[], debug=False):
		found_values = []
		names = [TripleObj(var_name, file_reader, token)]

		def inner():
			nonlocal found_values, names
			new_names = []
			for obj in names:
				name = obj.name
				file_reader = obj.file_reader
				token = obj.token

				# Extract the information we need from the token --> passing the token is faster for the user
				clss_name 	= token['clssName']
				func_name 	= token['funcName']
				funcId		= token['funcID']
				instr 		= token['instr']

				if debug:
					print(f'\nTARGET\t{name}\tTARGET')

				# Run the tests on name
				# At the end, update found_values and names accordingly
				# Stop execution when names becomes empty?
				try:
					########################################
					#               A. Value               #
					########################################

					if is_string(name) or is_number(name) or is_allowed_value(name, allowed):
						found_values.append(name)

						if debug:
							print('----------FOUND----------')
							print(name)
							print('-------------------------\n\n')

						continue # -> found and saved

					if is_class_instance(name):
						without_this = name.replace('this.', '')

						this_setter = Common.search_keywords(file_reader, [f'{name}=', f'{name} =', f'{without_this} =', f'{without_this}='])

						for t in this_setter:
							new_name = t['value'].split('=')[1].strip(' ;')
							new_names.append(TripleObj(new_name, file_reader, t))

							if debug:
								print(f'INSTR:\t {instr}')
								print('SCOPE:\tCLASS INSTANCE')

						continue

					########################################
					#            C. Method call            #
					########################################

					# 1. Search through the current parameters of the function call --> add them to the new_names list
					# 2. Get the return value of this method

					if Common.is_method_call(name):

						# # 1.
						# # Search through the arguments of the function (usually the name is passed there)
						# methods_args = Common.get_method_args(name)
						# for arg in methods_args:
						# 	new_names.append(TripleObj(arg, cpy(file_reader), token))


						# # 2.
						# # Find the return value of this method
						# # print(Common.get_classes_and_funcs(file_reader))
						# print('\n******************************************************************************')
						# print(name.split('(', 1)[0])
						# print('******************************************************************************\n')

						if debug:
							print(f'INSTR:\t {instr}')
							print('SCOPE:\tMETHOD CALL --> Not yet analysis available')

						continue # Add new names to analyse on the next function call / iteration

					########################################
					#             B. Variable              #
					########################################
					# FixMeLater: -> CHECK SCOPE does not seem to be deterministic...

					# It is argument of the current method
					# - Search for when this function is called and get the param value at the same index
					# Get current function and package informations
					func, filter_package = Common.get_file_pkg(file_reader, clss_name, func_name)
					if func != None:
						# Get arg position in function call
						func_args = Common.get_func_args(func['instr'])
						# Get argument position index
						index = Common.get_position_index(func_args, " "+name)

						if index < 0:
							# Check in scope
							scope_names = Common.check_scope(file_reader, name, funcId, instr)
							for scope_name in scope_names:
								new_names.append(TripleObj(scope_name, cpy(file_reader), token))

							if debug:
								print(f'INSTR:\t {instr}')
								print('SCOPE:\tCHECK SCOPE')
							
							continue

						# Filter out all the java files using SPECK technique based on package import
						filtr = Filter(directory, Rules.extractPkgNames(filter_package)) 
						filteredJavaFiles = filtr.execute()

						# It may be that some files are non considered (e.g. if the package is not imported because the files are in the same package)
						# Thus, use grep to search for func usage throughout the project

						# Run grep and save result in tmp.txt
						os.system(f"grep -r -e '{clss_name}' {directory}/sources/ | egrep '{func_name}(\(| \()' > tmp.txt")

						# The following is used to add additional files which are not considered so fat
						os.system(f"egrep -r -e '\.{func_name}(\(| \()' {directory}/sources/ >> tmp.txt")

						# Read tmp.txt
						tmp_file = open('tmp.txt', 'r')
						tmp_file_content = tmp_file.readlines()

						# Close and delete tmp.txt
						tmp_file.close()
						os.system("rm tmp.txt")

						# Get java filenames
						for tmp_line in tmp_file_content:
							check_same_line = tmp_line.split(':', 1)[1].strip()
							if check_same_line == instr:
								continue
							filteredJavaFiles.append(tmp_line.split()[0].strip(" :"))

						# Improve performance not repeating the same files
						filteredJavaFiles = Common.get_unique(filteredJavaFiles)
						
						findings = [] # store all the valid names found

						# Search throughout the project
						for javaFile in filteredJavaFiles:
							f_reader = FileReader(javaFile)	# current file

							# Get arg value of the function
							# f_reader is the current file, func_name is the function we want to be called, index is the position of the argument we are interested into
							arg_values = Common.get_all_arg_names(f_reader, func_name, index)
							for arg in arg_values:
								new_names.append(TripleObj(arg['value'], f_reader, arg))


						if debug:
							print(f'INSTR:\t {instr}')
							print('SCOPE:\tARGUMENT OF METHOD')
							
						continue

					else:
						# Check in scope
						scope_names = Common.check_scope(file_reader, name, funcId, instr)
						for scope_name in scope_names:
							new_names.append(TripleObj(scope_name, cpy(file_reader), token))

						if debug:
							print(f'INSTR:\t {instr}')
							print('SCOPE:\tCHECK SCOPE')
						
						continue

					raise CustomError(f'\n\nNothing happened for {name}\nINSTR:\t{instr}\n\n')
				except CustomError as e:
					if debug:
						print(e)

			# Update target name values for next call

			new_names = remove_casting(new_names)
			new_names = get_unique_names(new_names)
			new_names = remove_found_duplicates(new_names, found_values)
			arr = []
			for nn in new_names:
				flag = False
				for n in names:
					if flag: break 
					flag = nn.equals(n)
				if not flag:
					arr.append(nn)

			new_names = arr

			if debug:
				print_names = []
				for n in new_names:
					print_names.append(n.name)

				print(f'\n\nNEXT: {print_names}')
				print(f'\n\nFOUND: {found_values}')

			names = new_names.copy()
			return names, found_values
		return inner


	@staticmethod
	def chase_value(file_reader, directory, name, token, allowed=[], debug=False):
		o = Common.chase_value_outer(file_reader, directory, name, token, allowed, debug)
		triple_obj, found_values = o()

		for i in range(len(triple_obj)):
			triple_obj, found_values = o()

			# for qwe in triple_obj:
			# 	print('names.name =', qwe.name)
			# 	print('names.file_reader =', qwe.file_reader)
			# 	print('names.token =', qwe.token)
			# print('found_values =', found_values)

		if len(found_values) > 0:				# if something is found...
			return found_values			# ...return (True, values)
		else:
			return None



		