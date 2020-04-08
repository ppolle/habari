import traceback

def error_to_string(error):
	message = "Exception: {0} Error: {1} Traceback: {2}".format(type(error), error, traceback.format_exc())
	return message