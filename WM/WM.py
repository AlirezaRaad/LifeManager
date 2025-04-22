import os

import numpy as np
import pandas as pd
import psycopg2 as psql
from dotenv import load_dotenv
from psycopg2 import sql
from psycopg2.errors import DuplicateDatabase


class WorkManager:
    def __init__(self):
        load_dotenv()
        self.MakePsqlDB()

    def MakePsqlDB(self) -> bool:
        """Make a PostgresSql database based on .env "PSQ_*" parameters

        Returns:
            _type_: bool
        """
        conn_params = {
            "dbname": "postgres",  # Connect to the default 'postgres' database
            "user": os.environ["PSQL_USER"],
            "password": os.environ["PSQL_PASSWORD"],  # Set to your password if required
            "host": os.environ["PSQL_HOST"],
            "port": os.environ["PSQL_PORT"],
        }
        try:
            # Connect to the PostgreSQL server
            conn = psql.connect(**conn_params)
            conn.autocommit = True  # Enable autocommit for CREATE DATABASE

            cursor = conn.cursor()

            # Create the new database
            cursor.execute(
                sql.SQL("CREATE DATABASE {}").format(sql.Identifier("workmanager"))
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
