from typing import Literal

class LiferManager:
    def __init__(self, minconn: int, maxconn: int): ...
    @property
    def config(self) -> dict: ...
    def __cursor(self):
        """ "Makes A cursor pool and a yields cursor from the pool."""
        ...

    def MakePsqlDB(self) -> bool:
        """Make a PostgresSql database based on .env "PSQ_*" parameters

        Returns:
            _type_: bool
        """
        ...

    def DailyTasksTable(self, task_name: str = None, ref_to: str = None) -> bool:
        """This Method adds task to the task table. For example you might add 'Udemy' subtask to 'Learning' main task.
            **NOTE: IT WILL MAKE A PARENT IF ref_to=None**
            **NOTE: It will return False If you entered a ref_to that does not exist. First You need to add it manually.**

        Args:
            task_name (str): This is the subtask.(could be main if task_parent is None)
            ref_to (str): This is the task that you would refer to.

        Example:
            DailyTasksTable(task_name= 'Learning') -> This make a parent 'Learning' that others can refer to.

            DailyTasksTable(task_name= 'Udemy', ref_to='Learning') -> this makes 'Udemy' child of 'Learning'

        Returns:
            bool: returns True if making task was successful
        """
        ...

    def _CreateDailyTasksTable(self) -> bool:
        """This Method makes Tasks Table in the database

        Returns:
            bool: True if it  successfully built it and False if it fails.
        """

    def __AllParentTasks(self) -> list:
        """This Method Will return a Literal object containing every PARENT in the dailytask TABLE.

        Returns:
            list: A list Obj.
        """
        ...

    def MakeWeeklyTables(self) -> bool:
        """
        Makes a Table with the current year & week name is it.

        Assume we are in the week 16 of 2025, it makes a y2025w16 table.


        Returns:
            bool: True if it successfully make the table and False otherwise.
        """
        ...

    def ShowAllTables(
        self,
        table_schema: str = "public",
        table_type: Literal[
            "BASE TABLE", "VIEW", "FOREIGN TABLE", "LOCAL TEMPORARY"
        ] = "BASE TABLE",
    ) -> str | bool:
        """
        Returns a str containing all of the tables using the provided schema and TABLE type.

        Args:
            table_schema (str, optional): Defaults to "public".
            table_type (str, optional):  Defaults to "BASE TABLE".
        """
        ...

    def InsertIntoWeeklyTable(
        self, duration: float, task_id: int, description: str = None
    ) -> bool: ...
