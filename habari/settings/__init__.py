import sys

if 'runserver' in sys.argv:
	from habari.settings.local import *
else:
	from habari.settings.prod import *