import sys

if 'test' in sys.argv:
    from habari.settings.test import *
else:
    from habari.settings.dev import * 
