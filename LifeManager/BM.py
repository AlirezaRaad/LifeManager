import datetime as dt
import os
from collections import deque
from typing import List, Optional, Tuple

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib import colormaps
from psycopg2.errors import CheckViolation, DuplicateFunction, UniqueViolation
from sqlalchemy import create_engine, text

from .Cursor import Cursor
from .logger_config import logger


class CBanker(Cursor):
    def __init__(self, minconn=1, maxconn=10):
        super().__init__(minconn, maxconn)

    def __fetch_bank_id(self, bank_name) -> int | bool:
        with self._cursor() as cursor:
            cursor.execute("""SELECT id FROM banks WHERE bankname = %s""", (bank_name,))
            answer = cursor.fetchone()
            if answer is None:
                return False
            return answer[0]

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

    def make_transaction(
        self,
        bank_name: str,
        amount: float,
        expense_type: str,
        description: str | None = None,
    ):
        expense_id = self.fetch_expense_id(expense_name=expense_type)
        if not expense_id:
            logger.error(f"an error with fetching {expense_type} from DataBase.")
            return False

        bank_id = self.__fetch_bank_id(bank_name=bank_name)
        if not bank_id:
            logger.error(f"{bank_name} doesn't exists in the banks TABLE")
            return False

        with self._cursor() as cursor:
            try:
                cursor.execute(
                    """INSERT INTO banker (bankid, amount, description, expenseType) VALUES (%s,%s,%s,%s)""",
                    (bank_id, amount, description, expense_id),
                )
                return True
            except CheckViolation:
                #! NEGATIVE balance.
                logger.exception("The Balance was about to get NEGATIVE.")
                return False

    def fetch_expense_id(self, expense_name) -> int | bool:
        with self._cursor() as cursor:
            cursor.execute(
                """SELECT id FROM bankexpensetype WHERE expensename = %s""",
                (expense_name,),
            )
            answer = cursor.fetchone()
            if answer is None:
                return False
            return answer[0]

    def add_expense(self, expense_name, ref_to=None) -> bool:

        if ref_to is None:

            if expense_name not in self._get_all_parent_expenses():
                with self._cursor() as cursor:
                    try:
                        cursor.execute(
                            "INSERT INTO bankexpensetype (expenseName) VALUES (%s)",
                            (expense_name,),
                        )
                        logger.info(
                            f"added {expense_name} as parent expense in bankexpensetype TABLE."
                        )
                        return True
                    except UniqueViolation:
                        return True

                    except Exception:
                        logger.exception(
                            f"An error occurred when adding parent task of {expense_name} to the bankexpensetype TABLE."
                        )
                        return False
            else:
                return True  # The parent task already there so it is TRue
        with self._cursor() as cursor:
            try:
                # ? First We Have to Fetch parent id:
                cursor.execute(
                    "SELECT id FROM bankexpensetype WHERE expenseName = %s;", (ref_to,)
                )
                parent_id = cursor.fetchone()[0]

                # ? Now its time to add expense_name and with its parent_id to the TABLE.
                cursor.execute(
                    "INSERT INTO bankexpensetype (expenseName,parentexpenseid) VALUES(%s,%s);",
                    (expense_name, parent_id),
                )
                return True

            except UniqueViolation:
                return True

            except Exception:
                logger.exception(
                    f"There is an error in adding {expense_name} to the banks TABLE with {ref_to} as its parent."
                )
                return False

    def _get_all_parent_expenses(self) -> list:

        with self._cursor() as cursor:
            cursor.execute(
                "SELECT expensename FROM bankexpensetype WHERE parentexpenseid is null;"
            )

            return [i[0] for i in cursor.fetchall()]

    def _get_all_child_expenses(self, parent_name) -> list:

        parent = int(self.fetch_expense_id(parent_name))
        with self._cursor() as cursor:
            cursor.execute(
                "SELECT expensename FROM bankexpensetype WHERE parentexpenseid = %s;",
                (parent,),
            )

            return [i[0] for i in cursor.fetchall()]

    def show_all_banks(self):
        """Show All of the Banks."""

        with self._cursor() as cursor:
            cursor.execute("SELECT bankname FROM banks;")

            return [i[0] for i in cursor.fetchall()]

    def chart_it(self, last_x_days: int = 30):
        os.makedirs("figures", exist_ok=True)

        # % Cleaning any old figure, that it wont have been replace, due lack of data.
        # % The Above comment means that, assume I put the last_x_days = 10 and some of my bank were not active during
        # %  The 10 day so this method wont create any figure for or won't replace the old figure.

        # % So a bug will rise silently; If I first put last_x_days = 50, assume that 4 pics this method creates or replaces.
        # % Then I put last_x_days = 10, The program create or replace 2 pics. So in total we have 4 pics with different durations.

        # % And that why I implemented this list comprehension bellow.
        [
            os.remove(i) if os.path.exists(i) else None
            for i in {
                os.path.join(os.environ["FIGURES_PATH"], i)
                for i in [
                    j
                    for j in os.listdir(os.environ["FIGURES_PATH"])
                    if j.startswith("bank_")
                ]
            }
        ]

        with self._cursor() as cursor:
            cursor.execute("SELECT *  FROM bankexpensetype")
            _ = cursor.fetchall()

        mapping_idx = {i[0]: i[1] for i in _}

        engin = create_engine(
            f"postgresql://{os.environ["PGUSER"]}:{os.environ["PGPASSWORD"]}@{os.environ.get("PGHOST", "localhost")}:{os.environ.get("PGPORT", "5432")}/lifemanager",
            pool_size=10,
        )

        query = """SELeCT br.bankid,b.bankname, br.expensetype, bet.expensename, bet.parentexpenseid, 
                    br.amount,  br.balance, br.datetime, br.description  
                    FROM banker br JOIN banks b ON br.bankid = b.id JOIN bankexpensetype bet ON bet.id = br.expensetype;"""

        df = pd.read_sql(query, engin)

        # ~ Nows slcice the dataFrame of the last x days.

        df = df[
            df["datetime"] > (dt.datetime.now() - dt.timedelta(days=int(last_x_days)))
        ]

        # ~ Now lets make mapping dict for showing bank name.
        try:
            with self._cursor() as cursor:
                cursor.execute("SELECT *  FROM banks")
                _ = cursor.fetchall()

            mapping_banks = {i[0]: i[1] for i in _}
        except:
            logger.exception(f"An Error in creating mapping object for banks.")
            return False
        try:
            # ~ Now lets make mapping dict for showing expense name.
            with self._cursor() as cursor:
                cursor.execute("SELECT *  FROM bankexpensetype")
                _ = cursor.fetchall()

            mapping_idx = {i[0]: i[1] for i in _}
        except:
            logger.exception(f"An Error in creating mapping object for banks.")
            return False

        # ~ Now lets make the pie chart
        try:
            for _id in df["bankid"].unique():  #! Iterate of each bank.

                filtered_df = df[df["bankid"] == _id]
                data = filtered_df.groupby(df["parentexpenseid"])["amount"].sum()

                num_colors = df["parentexpenseid"].nunique()
                cmap = colormaps.get_cmap(cmap="Set3")
                colors = [cmap(i / num_colors) for i in range(num_colors)]

                plt.figure(figsize=(20, 10))
                plt.pie(
                    x=data,
                    labels=data.index.map(mapping_idx),
                    autopct="%1.2f%%",
                    startangle=90,
                    colors=colors,
                    textprops={"fontweight": "bold"},
                )
                plt.legend()
                plt.title(
                    f"What % You Spend on What in {mapping_banks[_id]} in last {last_x_days} days.",
                    fontsize=20,
                    fontweight="bold",
                )
                plt.savefig(fname=f"figures/bank_{mapping_banks[_id]}")
                logger.info(
                    f"PIE chart created successfully for {mapping_banks[_id]} BANK in last {last_x_days} days."
                )
            return True
        except:
            logger.exception(
                f"An error in making {mapping_banks[_id]} PIE CHART in last {last_x_days} days."
            )
            return False

    def fetch_records(
        self, bank_name, start_date: str, end_date: Optional[str] = None
    ) -> bool:

        bnk_id = self.__fetch_bank_id(bank_name=bank_name)
        if not bnk_id:
            return False

        try:
            start_date = dt.datetime.strptime(start_date, "%Y-%m-%d")

            if end_date is None:
                end_date = dt.datetime.now()
            else:
                end_date = dt.datetime.strptime(end_date, "%Y-%m-%d")
        except:
            logger.exception(
                "An Error while parsing the dates in Cbanker.fetch_records"
            )
            return False

        try:
            engin = create_engine(
                f"postgresql://{os.environ["PGUSER"]}:{os.environ["PGPASSWORD"]}@{os.environ.get("PGHOST", "localhost")}:{os.environ.get("PGPORT", "5432")}/lifemanager",
                pool_size=10,
            )
            query = text(
                """SELECT b.bankname, ext.expensename, br.amount, br.balance, br.datetime, br.description 
                FROM banker br JOIN BANKS b ON b.id = br.bankid JOIN bankexpensetype ext ON ext.id = br.expensetype 
                WHERE br.datetime < :end_date AND br.datetime > :start_date
                AND b.id = :bank_id"""
            )

            params = {"start_date": start_date, "end_date": end_date, "bank_id": bnk_id}
            df = pd.read_sql(query, engin, params=params)

        except:
            logger.exception("An Error while using cursor in Cbanker.fetch_records")
            return False

        try:
            fname = f"{bank_name} - {dt.datetime.now()}.xlsx"
            os.makedirs("Banking_records", exist_ok=True)
            path = os.path.join("Banking_records", fname)
            df.to_excel(path)
        except:
            logger.exception(
                "An Error Occurred While Saving bank records into excel in Cbanker.fetch_records. "
            )
            return False

        for filename in os.listdir("Banking_records"):
            file_path = os.path.join("Banking_records", filename)
            if filename != fname:
                os.remove(file_path)

        return True

    def bank_first_init_time(self, bank_name: str) -> bool | dt.datetime:
        bnk_id = self.__fetch_bank_id(bank_name=bank_name)
        if not bnk_id:
            return False

        with self._cursor() as cursor:
            cursor.execute(
                "SELECT datetime FROM banker WHERE bankid = %s LIMIT 1", (bnk_id,)
            )
            return cursor.fetchone()[0]
