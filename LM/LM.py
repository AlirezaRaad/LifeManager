import os

import numpy as np
import pandas as pd
import psycopg2 as psql
from dotenv import load_dotenv
from psycopg2 import sql
from psycopg2.errors import DuplicateDatabase


class LiferManager:
    def __init__(self):
        load_dotenv()
        self._psql_dbname = "workmanager"
        self._psql_user = os.environ["PSQL_USER"]
        self._psql_password = os.environ["PSQL_PASSWORD"]
        self._psql_host = os.environ["PSQL_HOST"]
        self._psql_port = os.environ["PSQL_PORT"]
        self.MakePsqlDB()

    def MakePsqlDB(self) -> bool:
        """Make a PostgresSql database based on .env "PSQ_*" parameters

        Returns:
            _type_: bool
        """
        conn_params = {
            "dbname": "postgres",  # Connect to the default 'postgres' database
            "user": self._psql_user,
            "password": self._psql_password,
            "host": self._psql_host,
            "port": self._psql_port,
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
        conn_params = {
            "dbname": self._psql_dbname,
            "user": self._psql_user,
            "password": self._psql_password,
            "host": self._psql_host,
            "port": self._psql_port,
        }
        try:
            psql.connect(**conn_params)
            return True
        except Exception as e:
            print(f"There was an error in TaskTable method -> {e}")
            return False
