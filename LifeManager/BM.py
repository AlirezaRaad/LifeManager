from collections import deque

from psycopg2 import sql
from psycopg2.errors import DuplicateFunction, DuplicateTable, UniqueViolation

from .LM import LifeManager
from .logger_config import logger


class CBanker:
    def __init__(self):
        self.__parent = LifeManager()
        self._cursor = self.__parent._cursor

    def make_banker_tables(self):

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

            return any(flags)

    def __make_banks_table(self):
        try:
            # GOAL: This Created The Table Banks for future foreign key.
            with self._cursor() as cursor:
                cursor.execute(
                    """CREATE TABLE banks (
                            id SERIAL PRIMARY KEY,
                            bankName TEXT UNIQUE NOT NULL
                        );"""
                )

        except DuplicateTable:
            return True

        except Exception:
            return False

    def __make_banker_table(self):
        with self._cursor() as cursor:
            flag = deque()
            try:
                # Create the banker table
                cursor.execute(
                    """CREATE TABLE banker (
                            id SERIAL PRIMARY KEY,
                            bankId INTEGER,
                            amount NUMERIC(11,2),
                            balance NUMERIC(11,2),
                            description TEXT,
                            CONSTRAINT FK_parent_bank FOREIGN KEY (bankId) REFERENCES banks(id),
                            CONSTRAINT no_minus_balance CHECK (balance >= 0)
                    );"""
                )
                flag.append(True)
            except DuplicateTable:
                flag.append(True)  # Table already exists
            except Exception as e:
                logger.exception("Error creating banker table:")
                cursor.connection.rollback()  # Roll back transaction
                return False

            try:
                # Create the trigger function
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
                            RETURN NEW;
                        END;
                    $$ LANGUAGE plpgsql;
                    """
                )
                flag.append(True)
            except DuplicateFunction:
                flag.append(True)  # Function already exists, proceed
            except Exception as e:
                logger.exception("Error creating banker trigger function: ")
                cursor.connection.rollback()  # Roll back transaction
                return False

            try:
                # Create the trigger
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
                logger.exception("Error creating banker trigger: ")
                cursor.connection.rollback()  # Roll back transaction
                return False

            # Commit the transaction if all steps succeed
            cursor.connection.commit()

            return all(flag)

    def add_bank(self, bank_name):
        """With This Method you can add a bank name to you database."""

        with self._cursor() as cursor:
            try:
                cursor.execute("INSERT INTO banks (bankname) VALUES (%s)", (bank_name,))
                logger.info(f"{bank_name} was added to banks TABLE.")
                return True
            except UniqueViolation:
                logger.info(
                    f"User Tried to add {bank_name} to banks TABLE but it was already exists."
                )
                return True
            except Exception:
                logger.exception(
                    f"There is an error in adding {bank_name} to the banks TABLE."
                )
                return False
