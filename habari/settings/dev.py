from .base import *

DEBUG = True

SECRET_KEY = config('SECRET_KEY')

# ==============================================================================
# Logging settings
# ==============================================================================

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(message)s'
        },
        'simple': {
            'format': '%(message)s'
        },
    },

    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
        'file': {
            'level': 'ERROR',
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'formatter': 'verbose',
            'when': 'D',
            'interval': 1,
            'backupCount': 10,
            'filename': os.path.join(BASE_DIR, 'logs/development.log')
        }
    },
    'loggers': {
        '': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
        }
    }
}