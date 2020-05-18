import traceback

def error_to_string(error, skip_traceback=False):
	message = "Exception: {0} Error: {1}".format(type(error), error)
	if skip_traceback:
		message += " Traceback: " + traceback.format_exc()
	return message

def http_error_to_string(error_code, url):
	message = "Http Error Code: {0} , Url: {1}".format(error_code,url)