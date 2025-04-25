import datetime as dt
import logging
import os
from contextlib import contextmanager

import numpy as np
import pandas as pd
import psycopg2 as psql
from dotenv import load_dotenv
from psycopg2 import sql
from psycopg2.errors import DuplicateDatabase, DuplicateTable
from psycopg2.pool import SimpleConnectionPool

# TODO: Make logger in every corner of the program for better understanding.

# * Make a every time this script runs.
os.makedirs("log", exist_ok=True)

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
handler = logging.FileHandler(
    f"log/main.py_{dt.datetime.now().strftime("%d-%m-%Y--%H-%M-%S")}.log")
handler.setFormatter(logging.Formatter(
    "%(asctime)s - %(levelname)s - %(message)s"))
logger.addHandler(handler)


class LiferManager:
    def __init__(self, minconn=1, maxconn=10):

        load_dotenv()
        self.__config = {"dbname": "workmanager",
                         "user": os.environ["PSQL_USER"],
                         "password": os.environ["PSQL_PASSWORD"],
                         "host": os.environ["PSQL_HOST"],
                         "port": os.environ["PSQL_PORT"]}

        self.MakePsqlDB()

        self._connection_pool = SimpleConnectionPool(
            minconn=minconn, maxconn=maxconn, **self.__config)

    @property
    def config(self):
        return self.__config

    @contextmanager
    def __cursor(self):

        conn = self._connection_pool.getconn()
        cursor = conn.cursor()

        try:
            yield cursor
            conn.commit()

        except Exception as e:
            conn.rollback()
            logger.exception("In @contextmanager's Exception")
            raise e

        finally:
            cursor.close()
            self._connection_pool.putconn(conn)

    def MakePsqlDB(self):

        #! NOTE: I specifically DID NOT use connection pool for this one because I the dbname is set to postgres and
        #! this method is a kick start for the database creation and What pool should give to a db that it isn't created
        #! Yet! LOL

        conn_params = {
            "dbname": "postgres",  # Connect to the default 'postgres' database
            "user": self.config["user"],
            "password": self.config["password"],
            "host": self.config["host"],
            "port": self.config["port"],
        }
        try:
            # Connect to the PostgreSQL server
            conn = psql.connect(**conn_params)
            conn.autocommit = True  # Enable autocommit for CREATE DATABASE

            cursor = conn.cursor()

            # Create the new database
            cursor.execute(
                sql.SQL("CREATE DATABASE workmanager;")
            )

            logger.info(f"Postgres Database initiated successfully!")
            return True

        except DuplicateDatabase:

            logger.info("Database is already initiated")
            return True

        except Exception as e:
            logger.exception(
                f"In database creation")
            return False

        finally:
            cursor.close()
            conn.close()

    def DailyTasksTable(self, task_name, task_parent=None) -> bool:

        if not self._CreateDailyTasksTable():
            logger.critical(
                f"In DailyTasksTable WHEN it was Calling _CreateDailyTasksTable Method.")
            return False  # ? It means that if the table creation fails, this method will fail as well

        try:
            with self.__cursor() as cursor:
                pass
            return True

        except Exception as e:

            logger.exception(f"In DailyTasksTable method")
            return False

    def _CreateDailyTasksTable(self) -> bool:

        with self.__cursor() as cursor:
            try:
                cursor.execute(
                    f"CREATE TABLE DailyTasks (id SERIAL PRIMARY KEY, taskName TEXT, parentTaskId INTEGER, FOREIGN KEY (parentTaskId) REFERENCES DailyTasks(id));")
                return True

            except DuplicateTable:
                return True

            except Exception as e:
                logger.exception(
                    f"In _CreateDailyTasksTable Method:")

                return False
