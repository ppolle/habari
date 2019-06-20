import sys

if 'test' in sys.argv:
    from sly.settings.test import *
else:
    from sly.settings.dev import * 
