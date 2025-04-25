import os
from contextlib import contextmanager

import numpy as np
import pandas as pd
import psycopg2 as psql
from dotenv import load_dotenv
from psycopg2 import sql
from psycopg2.errors import DuplicateDatabase
from psycopg2.pool import SimpleConnectionPool


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
            raise e

        finally:
            cursor.close()
            self._connection_pool.putconn(conn)

    def MakePsqlDB(self) -> bool:
        """Make a PostgresSql database based on .env "PSQ_*" parameters

        Returns:
            _type_: bool
        """
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
                sql.SQL("CREATE DATABASE {}").format(
                    sql.Identifier("workmanager"))
            )

            print(f"Postgres Database initiated successfully!")
            return True
        except DuplicateDatabase:
            print("Database is already initiated")
            return True

        except Exception as e:
            print(f"An error has been occurred in database creation : {e}")
            return False

        finally:
            cursor.close()
            conn.close()

    def TaskTable(self, task_name, task_parent) -> bool:
        """This Method adds task to the task table. For example you might add 'Udemy' subtask to 'Learning' main task.
            **NOTE: IT WILL MAKE A PARENT IF THERE IS NONE**

        Args:
            task_name (str): This is the subtask.
            task_parent (str): This is the main task. 

        Returns:
            bool: returns True if making task was successful
        """

        try:
            with self.__cursor() as cursor:
                print("Ye Buddy")

            return True

        except Exception as e:

            print(f"There was an error in TaskTable method -> {e}")
            return False

    def _CreateTaskTable(self) -> bool:
        """This Method makes Tasks Table in the database

        Returns:
            bool: True if it  successfully built it and False if it fails.
        """
        return False
