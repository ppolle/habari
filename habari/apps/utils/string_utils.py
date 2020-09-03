import re
import string

def unslugify_text(text):
	""" Unslugify slugs """
	return re.sub(r'-',' ',text)

def printable_text(text):
    '''Make sure only printable characters are displayed'''
    return "".join(filter(lambda x: x in set(string.printable), text.replace('-',' ')))
