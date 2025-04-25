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
        self.psql_dbname = "workmanager"
        self.psql_user = os.environ["PSQL_USER"]
        self.psql_password = os.environ["PSQL_PASSWORD"]
        self.psql_host = os.environ["PSQL_HOST"]
        self.psql_port = os.environ["PSQL_PORT"]
        self.MakePsqlDB()

    def MakePsqlDB(self) -> bool:
        """Make a PostgresSql database based on .env "PSQ_*" parameters

        Returns:
            _type_: bool
        """
        conn_params = {
            "dbname": "postgres",  # Connect to the default 'postgres' database
            "user": self.psql_user,
            "password": self.psql_password,
            "host": self.psql_host,
            "port": self.psql_port,
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

    def TaskTable(self):
        pass
