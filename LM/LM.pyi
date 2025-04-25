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

    def TaskTable(self, task_name: str, task_parent: str) -> bool:
        """This Method adds task to the task table. For example you might add 'Udemy' subtask to 'Learning' main task.
            **NOTE: IT WILL MAKE A PARENT IF THERE IS NONE**

        Args:
            task_name (str): This is the subtask.
            task_parent (str): This is the main task. 

        Returns:
            bool: returns True if making task was successful
        """
        ...

    def _CreateTaskTable(self) -> bool:
        """This Method makes Tasks Table in the database

        Returns:
            bool: True if it  successfully built it and False if it fails.
        """
