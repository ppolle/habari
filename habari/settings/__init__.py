import sys

if 'runserver' in sys.argv:
	from sly.settings.local import *
else:
	from sly.settings.prod import *