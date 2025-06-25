import os
from collections import deque
from contextlib import contextmanager

import psycopg2 as psql
from dotenv import load_dotenv
from psycopg2 import sql
from psycopg2.errors import (
    DuplicateDatabase,
    DuplicateFunction,
    DuplicateTable,
    UniqueViolation,
)
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
        self._create_daily_tasks_table()
        self.make_tables()

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

    # % LM TABLES
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

    def _create_daily_tasks_table(self) -> bool:

        with self._cursor() as cursor:
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
                    f"In _create_daily_tasks_table Method You have Duplicate Key: "
                )
                return True
            except Exception as e:
                logger.exception(f"In _create_daily_tasks_table Method:")

                return False

    # % BM TABLES
    def make_tables(self):

        flags = deque()

        with self._cursor() as cursor:
            # ? Check to see if banks TABLE exists or not
            cursor.execute(
                """SELECT EXISTS (
                    SELECT FROM pg_tables 
                    WHERE schemaname = 'public' 
                    AND tablename = 'banks'
                ) AS table_exists;"""
            )
            answer = cursor.fetchone()[0]

            if answer:
                flags.append(answer)
            else:
                flags.append(self.__make_banks_table())

            # ? Creating bank expense type TABLE.
            flags.append(self.__create_bank_expense_type_table())

            # ? Check to see if banker TABLE exists or not
            cursor.execute(
                """SELECT EXISTS (
                    SELECT FROM information_schema.triggers 
                    WHERE event_object_schema = 'public' 
                    AND event_object_table = 'banker' 
                    AND trigger_name = 'change_balance_on_insert_trigger'
                ) AS trigger_exists;
                """
            )
            answer = cursor.fetchone()[0]

            if answer:

                flags.append(answer)
            else:

                flags.append(self.__make_banker_table())

            return all(flags)

    def __make_banks_table(self):
        try:
            # GOAL: This Created The Table Banks for future foreign key.
            with self._cursor() as cursor:
                cursor.execute(
                    """CREATE TABLE IF NOT EXISTS banks (id SERIAL PRIMARY KEY,bankName TEXT UNIQUE NOT NULL);"""
                )

                cursor.execute(
                    """
                    CREATE OR REPLACE FUNCTION lowercase_name()
                    RETURNS TRIGGER AS $$
                    BEGIN
                        NEW.bankName := LOWER(NEW.bankName);
                        RETURN NEW;
                    END;
                    $$ LANGUAGE plpgsql;
                """
                )

                cursor.execute(
                    """
                    DO $$
                    BEGIN
                        IF NOT EXISTS (
                            SELECT 1 FROM pg_trigger WHERE tgname = 'trg_lowercase_name'
                        ) THEN
                            CREATE TRIGGER trg_lowercase_name
                            BEFORE INSERT OR UPDATE ON banks
                            FOR EACH ROW
                            EXECUTE FUNCTION lowercase_name();
                        END IF;
                    END;
                    $$;
                """
                )
                return True

        except Exception:
            return False

    def __make_banker_table(self):
        with self._cursor() as cursor:
            flag = deque()
            try:
                logger.info("Creating banker TABLE...")
                cursor.execute(
                    """CREATE TABLE IF NOT EXISTS banker (
                            id SERIAL PRIMARY KEY,
                            bankId INTEGER,
                            expenseType INT,
                            amount NUMERIC(11,2),
                            balance NUMERIC(11,2),
                            dateTime TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            description TEXT,
                            CONSTRAINT FK_parent_bank FOREIGN KEY (bankId) REFERENCES banks(id),
                            CONSTRAINT no_minus_balance CHECK (balance >= 0),
                            CONSTRAINT FK_expense_type FOREIGN KEY (expenseType) REFERENCES bankexpensetype(id)
                    );"""
                )
                flag.append(True)

            except Exception:
                logger.exception("Error in creating banker table:")
                cursor.connection.rollback()  # Roll back transaction
                flag.append(False)

            try:

                logger.info("Creating trigger function for banker TABLE...")
                cursor.execute(
                    """
                    CREATE OR REPLACE FUNCTION change_balance_on_insert()
                        RETURNS TRIGGER AS $$
                        DECLARE lastBalance NUMERIC;
                        BEGIN
                            SELECT balance INTO lastBalance 
                            FROM banker 
                            WHERE bankId = NEW.bankId 
                            ORDER BY id DESC 
                            LIMIT 1;
                            NEW.balance := COALESCE(lastBalance, 0) + NEW.amount;

                            IF lastBalance IS NULL THEN
                                NEW.description := 'First Initial';
                            END IF;

                            RETURN NEW;
                        END;
                    $$ LANGUAGE plpgsql;
                    """
                )
                flag.append(True)
            except DuplicateFunction:
                flag.append(True)  # Function already exists, proceed
            except Exception as e:
                logger.exception(
                    "Error creating banker trigger function for banker TABLE: "
                )
                cursor.connection.rollback()  # Roll back transaction
                flag.append(False)

            try:
                # Create the trigger
                logger.info("Creating trigger for banker TABLE...")
                cursor.execute(
                    """
                    CREATE OR REPLACE TRIGGER change_balance_on_insert_trigger
                        BEFORE INSERT
                        ON banker
                        FOR EACH ROW
                        EXECUTE FUNCTION change_balance_on_insert();
                    """
                )
                flag.append(True)
            except Exception as e:
                logger.exception("Error creating a trigger for banker : ")
                cursor.connection.rollback()
                flag.append(False)

            try:
                logger.info(
                    "Committing transaction on making banker TABLE,FUNCTION,TRIGGER..."
                )
                cursor.connection.commit()
            except Exception as e:
                logger.exception(
                    "Error committing transaction on making banker TABLE,FUNCTION,TRIGGER: "
                )
                cursor.connection.rollback()
                return False

            result = all(flag)
            if not result:
                logger.info(
                    "One or more operations failed in making banker TABLE,FUNCTION,TRIGGER! Returning False."
                )
            return result

    def __create_bank_expense_type_table(self):

        with self._cursor() as cursor:
            try:
                # GOAL: This Created The Table with Unique Constrain on both columns but not (expenseName,NULL)
                cursor.execute(
                    """CREATE TABLE IF NOT EXISTS bankexpensetype (id SERIAL PRIMARY KEY, expenseName TEXT UNIQUE, parentExpenseId INTEGER,
                            CONSTRAINT FK_self_parent_expense FOREIGN KEY (parentExpenseId) REFERENCES bankexpensetype(id),
                            CONSTRAINT unique_expense_rows UNIQUE(expenseName, parentExpenseId));"""
                )

                # GOAL: Now I manually made (expenseName,NULL) a UNIQUE.
                cursor.execute(
                    """CREATE UNIQUE INDEX IF NOT EXISTS unique_null_parent_expense ON bankexpensetype(expenseName) WHERE parentExpenseId IS NULL;"""
                )
                return True

            except:
                logger.exception("An Error in creating BankExpenseType TABLE")
                return False
