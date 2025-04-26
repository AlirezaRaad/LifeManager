class LiferManager:
    def __init__(self, minconn: int, maxconn: int):
        ...

    @property
    def config(self) -> dict:
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

    def _CreateTaskTable(self) -> bool:
        """This Method makes Tasks Table in the database

        Returns:
            bool: True if it  successfully built it and False if it fails.
        """
