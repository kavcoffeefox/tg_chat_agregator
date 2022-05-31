import logging
import json
import os

# API CONST
BASE_URL_PART = "/organizer/api/1.0"

# DB CONST
TEST_TIME = 60
TEST_USE_LIMIT = 10
PROD_USE_LIMIT = 99
TWELVE_HOUR_IN_SECOND = 43200
USE_LIMIT = TEST_USE_LIMIT
PERIOD_BETWEEN_USE_SESSION = TWELVE_HOUR_IN_SECOND
PERIOD_ACTIVE_JOB = TEST_TIME

SESSION_DB = 'tgsessions.sqlite'

SQLITE_DB_NAME = 'tg_cht_org_db.sqlite'

SQLITE_DATABASE = "sqlite"
POSTGRES_DATABASE = "postgres"

DATABASE_TYPE = SQLITE_DATABASE

# OTHER CONST
POSTGRES_CONFIG_FILE = "pgconnection.json"

FILE_FOR_SAVE_ACTIVE_JOB = "active_job"


"""
Database config
"""
postgres_config = None
if os.path.exists(POSTGRES_CONFIG_FILE):
    with open(POSTGRES_CONFIG_FILE) as file:
        postgres_config = json.load(file)

"""
Logging
"""


class FileHandler(logging.Handler):
    def __init__(self, filename):
        logging.Handler.__init__(self)
        self.filename = filename

    def emit(self, record):
        message = self.format(record)
        with open(self.filename, 'a') as file:
            file.write(message + '\n')


class FileFilter(logging.Filter):
    def filter(self, record):
        if record.levelno >= 40:
            return True
        else:
            return False


logging_config = {
    'version': 1,
    'disable_existing_loggers': False,

    'formatters': {
        'std_format': {
            'format': '{asctime} - {levelname} - {name} - {message}',
            'style': '{'
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'INFO',
            'formatter': 'std_format',
            'filters': ['file_filter', ]
        },
        'file': {
            '()': FileHandler,
            'level': 'INFO',
            'filename': 'debug.log',
            'formatter': 'std_format'
        }
    },
    'loggers': {
        'app_logger': {
            'level': logging.INFO,
            'handlers': ['console', 'file']
        }
    },
    'filters': {
        'file_filter': {
            '()': FileFilter
        }
    }
}
