import psycopg2
from psycopg2 import extensions
import sqlite3
import datetime
from abc import ABCMeta, abstractmethod
from typing import Optional, Union

from persist.sql_queries import *

from settings import *

import logging.config

logging.config.dictConfig(logging_config)

logger = logging.getLogger('app_logger')


class DBInitFailed(Exception):
    pass


class MockConnection:
    class Cursor:
        def execute(self, *args, **kwargs):
            for item in args:
                print(item)
            for key, item in kwargs.items():
                print(f"{key}: {item};")

    def cursor(self) -> Cursor:
        return MockConnection.Cursor()


class PostgressConnection:

    def _get_connection(self) -> Union[psycopg2.extensions.connection, sqlite3.Connection, MockConnection]:
        try:
            connection = psycopg2.connect(
                database=postgres_config["database"],
                user=postgres_config["user"],
                password=postgres_config["password"],
                host=postgres_config["host"],
                port=postgres_config["port"]
            )
            return connection
        except Exception as e:
            logger.critical("ERROR: ", exc_info=e)
            raise DBInitFailed


class SQLiteConnection:

    def _get_connection(self) -> Union[psycopg2.extensions.connection, sqlite3.Connection, MockConnection]:
        try:
            connection = sqlite3.connect(SQLITE_DB_NAME)
            return connection
        except Exception as e:
            logger.critical("ERROR: ", exc_info=e)
            print(e)
            raise DBInitFailed
