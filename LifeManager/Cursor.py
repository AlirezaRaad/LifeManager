import os
from contextlib import contextmanager

import psycopg2 as psql
from dotenv import load_dotenv
from psycopg2 import sql
from psycopg2.pool import SimpleConnectionPool

from .logger_config import logger


class Cursor:
    def __init__(self, minconn=1, maxconn=10):

        load_dotenv()

        self._config = {
            "dbname": "lifemanager",
            "user": os.environ["PGUSER"],
            "password": os.environ["PGPASSWORD"],
            "host": os.environ["PGHOST"],
            "port": os.environ["PGPORT"],
        }
        self.make_psql_db()
        self._connection_pool = SimpleConnectionPool(
            minconn=minconn, maxconn=maxconn, **self._config
        )

    @contextmanager
    def _cursor(self):

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

    def make_psql_db(self):

        #! NOTE: I specifically DID NOT use connection pool for this one because I the dbname is set to postgres and
        #! this method is a kick start for the database creation and What pool should give to a db that it isn't created
        #! Yet! LOL

        conn_params = {
            "dbname": "postgres",  # Connect to the default 'postgres' database
            "user": self._config["user"],
            "password": self._config["password"],
            "host": self._config["host"],
            "port": self._config["port"],
        }
        try:
            conn = psql.connect(**conn_params)
            conn.autocommit = True  # Enable autocommit for CREATE DATABASE

            cursor = conn.cursor()

            # Create the new database
            cursor.execute(sql.SQL("CREATE DATABASE lifemanager;"))

            logger.info(f"Postgres Database initiated successfully!")
            return True

        except DuplicateDatabase:

            logger.info("Database is already initiated")
            return True

        except Exception as e:
            logger.exception(f"In database creation")
            return False

        finally:
            cursor.close()
            conn.close()
