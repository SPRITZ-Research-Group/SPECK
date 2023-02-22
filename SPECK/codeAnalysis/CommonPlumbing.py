#!/usr/bin/python3
from copy import copy as cpy
import re
import Common


class TripleObj():
	def __init__(self, name, file_reader, token):
		self.name = name
		self.file_reader = cpy(file_reader)
		self.token = token

	def equals(self, other):
		if self.name == other.name and self.token == other.token:
			return True
		return False


class CustomError(Exception): 
    def __init__(self, value): 
        self.value = value
    def __str__(self): 
        return "ERROR: %s" % self.value


####################################################################################################
#                                       "Plumbing Functions"                                       #
####################################################################################################

####################################################################################################
#                                           CHASE_VALUE                                            #
####################################################################################################

########################################
#               A. Value               #
########################################

# Check if value is a string
def is_string(value):
	return value.startswith('"') and value.endswith('"')


# Check if value is a number (both int or float)
def is_number(value):
	return value.replace('.','',1).isdigit()


# Check if value is one of the "allowed" values
def is_allowed_value(value, values):
	for allowed in values:
		if value == allowed:
			return True
	return False


########################################
#             B. Variable              #
########################################
# Check if value is an instance of the current class
def is_class_instance(value):
	return value.startswith('this.') and not value.endswith(')')


# Extracts the value of a variable from its initialization line
# : -> visibility name = value;
def extract_var_value(var):
	splitted = var.split('=')
	if len(splitted) > 0:
		return splitted[1].replace(';', '').strip() # considering the ';' is only at the end
	return None


########################################
# Simplify names array in chase value  #
########################################

def remove_casting(triples):
	to_return = []
	for triple in triples:
		name = triple.name
		if len(name) > 0:
			if name[0] == '(':
				to_return.append(TripleObj(re.sub('^\(.*\) ', '', name), triple.file_reader, triple.token))
			else:
				to_return.append(triple)
	return to_return


def get_unique_names(names):
	unique_names = []
	to_return = []
	for name in names:
		current_name = name.name
		if not current_name in unique_names and current_name != '':
			unique_names.append(current_name)
			to_return.append(name)
	return to_return


def remove_found_duplicates(triples, found):
	to_return = []
	for triple in triples:
		name = triple.name
		if name not in found:
			to_return.append(triple)
	return to_return


