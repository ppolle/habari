import re

def unslugify_text(text):
	""" Unslugify slugs """
	return re.sub(r'-',' ',text)