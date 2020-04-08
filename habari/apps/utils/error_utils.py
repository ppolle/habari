import traceback

def error_to_string(error, skip_traceback=False):
	message = "Exception: {0} Error: {1}".format(type(error), error)
	if skip_traceback:
		message += " Traceback: " + traceback.format_exc()
	return message