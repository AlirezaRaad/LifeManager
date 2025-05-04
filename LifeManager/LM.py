import datetime as dt
import logging
import os
import subprocess
from contextlib import contextmanager
from typing import Literal, Union
from uuid import UUID

import numpy as np
import pandas as pd
import psycopg2 as psql
from dotenv import load_dotenv
from psycopg2 import sql
from psycopg2.errors import (
    DuplicateDatabase,
    DuplicateTable,
    ForeignKeyViolation,
    InvalidTextRepresentation,
    UndefinedTable,
    UniqueViolation,
)
from psycopg2.pool import SimpleConnectionPool
from sqlalchemy import create_engine
from sqlalchemy.exc import ProgrammingError

from .custom_timer import CTimer

# * Make a every time this script runs.
from .logger_config import logger

# TODO: at the end, make a single method to all the tables in a single go. it would be beneficial, I think?


class LifeManager:

    def __init__(self, minconn=1, maxconn=10):

        load_dotenv()
        self.__config = {
            "dbname": "workmanager",
            "user": os.environ["PGUSER"],
            "password": os.environ["PGPASSWORD"],
            "host": os.environ["PGHOST"],
            "port": os.environ["PGPORT"],
        }

        self.MakePsqlDB()

        self._connection_pool = SimpleConnectionPool(
            minconn=minconn, maxconn=maxconn, **self.__config
        )

        self.current_week_name = None

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
            cursor.execute(sql.SQL("CREATE DATABASE workmanager;"))

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

    def DailyTasksTableAdder(self, task_name: str, *, ref_to=None) -> bool:

        if not self._CreateDailyTasksTable():
            logger.critical(
                f"In DailyTasksTableAdder WHEN it was Calling _CreateDailyTasksTable Method."
            )
            return False  # ? It means that if the table creation fails, this method will fail as well

        # GOAL: If The referrer is None; Then if the task_name is not already a PARENT, It will make a parent row.
        if ref_to is None:
            if task_name not in self.__AllParentTasks():
                with self.__cursor() as cursor:
                    cursor.execute(
                        "INSERT INTO dailytasks (taskname) VALUES (%s)", (task_name,)
                    )
                    logger.info(f"Parent row {task_name} added successfully!")
                    return True

        try:
            with self.__cursor() as cursor:

                # GOAL: This will fetch the PARENT id from db from the dailytasks.
                cursor.execute(
                    "SELECT id FROM dailytasks WHERE taskname = %s", (ref_to,)
                )
                parent_id = cursor.fetchone()[0]

                # GOAL: This will add the sub task to the TABLE.
                cursor.execute(
                    "INSERT INTO dailytasks (taskName, parentTaskId) VALUES (%s, %s)",
                    (task_name, parent_id),
                )

            return True

        except UniqueViolation:
            # CONCLUSION: Although Normally if would raise an error because od UNIQUE CONSTRAINT that I put, but here is will
            # CONCLUSION: return true because if this UniqueViolation occurs. it mean the user row is already in db and does not need to return False.
            logger.exception(f"In DailyTasksTableAdder method, A dupe Key: ")
            return True
        except Exception as e:

            logger.exception(f"In DailyTasksTableAdder method")
            return False

    def _CreateDailyTasksTable(self) -> bool:

        with self.__cursor() as cursor:
            try:
                # GOAL: This Created The Table with Unique Constrain on both columns but not (taskName,NULL)
                cursor.execute(
                    """CREATE TABLE dailytasks (id SERIAL PRIMARY KEY, taskName TEXT, parentTaskId INTEGER,
                            CONSTRAINT FK_self_parent_name FOREIGN KEY (parentTaskId) REFERENCES dailytasks(id),
                            CONSTRAINT unique_rows UNIQUE(taskName, parentTaskId));"""
                )

                # GOAL: Now I manually made (taskName,NULL) a UNIQUE.
                cursor.execute(
                    """CREATE UNIQUE INDEX unique_null_parent_task ON dailytasks(taskName) WHERE parentTaskId IS NULL;"""
                )

                return True

            except DuplicateTable:
                return True

            except UniqueViolation:
                logger.exception(
                    f"In _CreateDailyTasksTable Method You have Duplicate Key: "
                )
                return True
            except Exception as e:
                logger.exception(f"In _CreateDailyTasksTable Method:")

                return False

    def __AllParentTasks(self):
        with self.__cursor() as cursor:
            cursor.execute("SELECT * from dailytasks WHERE parentTaskId IS NULL")
            return [i[1] for i in cursor.fetchall()]

    def MakeWeeklyTables(self):
        date = dt.datetime.now().isocalendar()
        year, week = date.year, date.week

        self.current_week_name = f"y{year}w{week}"

        table_name = f"y{year}w{week}"

        with self.__cursor() as cursor:
            try:
                query = sql.SQL(
                    """CREATE TABLE IF NOT EXISTS {table} (
                                id SERIAL PRIMARY KEY, 
                                weekDay INT,
                                duration INT NOT NULL, 
                                taskID INT NOT NULL , 
                                description TEXT,
                                CONSTRAINT {const} FOREIGN KEY (taskID) REFERENCES dailytasks(id)
                                )
                                """
                ).format(
                    table=sql.Identifier(table_name),
                    const=sql.Identifier(f"FK_{table_name}_taskid"),
                )

                cursor.execute(query)
                logger.info(f"TABLE {table_name} has created successfully.")
                return True

            except:
                logger.exception(f"An Error occurred while making {table_name} TABLE: ")
                return False

    def ShowAllTables(
        self, table_schema: str = "public", table_type: str = "BASE TABLE"
    ) -> list | bool:

        try:
            with self.__cursor() as cursor:
                query = sql.SQL(
                    """
                    SELECT table_name FROM information_schema.tables 
                    WHERE table_schema = {schema} 
                    AND table_type = {ttype}
                    ORDER BY table_name
                """
                ).format(
                    schema=sql.Literal(table_schema), ttype=sql.Literal(table_type)
                )

                cursor.execute(query)
                tables = cursor.fetchall()

            return [x[0] for x in tables]
            return "\n".join(f"{i}. {j[0]}" for i, j in enumerate(tables, start=1))

        except:
            logger.exception("In ShowAllTables Method: ")
            return False

    def InsertIntoWeeklyTable(
        self, duration: float, task_id: int, description: str = None
    ) -> bool:

        self.MakeWeeklyTables()
        logger.info("Used MakeWeeklyTables Method in InsertIntoWeeklyTable")

        with self.__cursor() as cursor:
            s_i = sql.Literal

            try:
                query = sql.SQL(
                    "INSERT INTO {} (weekDay, duration, taskid, description) VALUES ({},{},{},{})"
                ).format(
                    sql.Identifier(self.current_week_name),
                    s_i(f"{dt.datetime.now().isocalendar().weekday}"),
                    s_i(f"{duration}"),
                    s_i(f"{task_id}"),
                    s_i(description),
                )
                cursor.execute(query)
                logger.info(
                    f"Inserted {duration} {task_id} {description} to the {self.current_week_name} TABLE."
                )
                return True
            except ForeignKeyViolation:
                logger.exception("InsertIntoWeeklyTable Violated a FK CONSTRAINT: ")
                return False
            except InvalidTextRepresentation:
                logger.exception("Entered TEXT instead of int for duration/task_id")
                return False

            except Exception:
                logger.exception("An Uncached Exception Has Happened:")
                return False

    def timer(self) -> UUID | bool:
        """Makes a CTimer object. Use the uid that it returns to access the CTimer object using CTimer.get_instance() and then use the instance methods.


        Returns:
            UUID | bool: Returns the made CTimer uid, otherwise False
        """
        # ! have to make a timer object
        try:
            _ = CTimer()
            return _.uid
        except Exception:
            logger.exception("In Making a CTimer Object in LM.timer Method.")
            return False

    def backup(self):

        os.makedirs("backup", exist_ok=True)
        timestamp = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = f"backup/workmanager_backup_{timestamp}.backup"

        command = [
            "pg_dump",
            "-F",
            "c",
            "-f",
            output_path,
            "workmanager",
        ]

        try:
            subprocess.run(command, check=True)
            logger.info(f"✅ Backup successful: {output_path}")
            return True
        except subprocess.CalledProcessError as e:
            logger.info(f"❌ Backup failed: {e}")
            return False

    def restore_backup(self, backup_path: Literal["latest"] = "latest") -> bool:

        if backup_path == "latest":
            backup_path = os.path.abspath(
                os.path.join("backup", sorted(os.listdir("backup"))[-1])
            )
        restore_command = (
            f"pg_restore  -d workmanager --clean --if-exists {backup_path}"
        )

        try:
            subprocess.run(restore_command, check=True, shell=True)
            logger.info(
                f"Database 'workmanager' restored successfully from {backup_path}."
            )
            return True
        except subprocess.CalledProcessError as e:
            logger.exception(f"Error occurred during restore: ")
            return False

    def fetch_all_rows(self, week: str = None) -> Union[pd.core.frame.DataFrame, bool]:

        if week is None:
            week = self.current_week_name
        try:
            engin = create_engine(
                f"postgresql://{os.environ["PGUSER"]}:{os.environ["PGPASSWORD"]}@{os.environ.get("PGHOST", "localhost")}:{os.environ.get("PGPORT", "5432")}/workmanager",
                pool_size=10,
            )

            query = f'SELECT * FROM "{week}"'
            logger.info(f"User Fetched {week} data.")
            return pd.read_sql(query, engin)

        except ProgrammingError as e:

            if isinstance(e.orig, UndefinedTable):
                logger.exception(
                    f"User tried to access a table '{week}' that is not in the DB."
                )
            else:
                logger.exception(f"An error occurred: {e}")
            return False

        except Exception:
            logger.exception(f"An error in fetch_all_rows")
            return False
