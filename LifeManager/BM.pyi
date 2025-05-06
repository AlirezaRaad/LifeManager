class CBanker:
    """
    This class handles creation and interaction with banking tables.
    """

    def __init__(self) -> None: ...
    def make_tables(self) -> bool:
        """
        This method creates banks and banker TABLES.

        Returns:
            bool: True if all tables were created or already exist, otherwise False.
        """
        ...

    def __make_banks_table(self) -> bool:
        """
        Internal method to create the banks table.

        Returns:
            bool: True if created or already exists, otherwise False.
        """
        ...

    def __make_banker_table(self) -> bool:
        """
        Internal method to create the banker table and its trigger/function.

        Returns:
            bool: True if created or already exists, otherwise False.
        """
        ...

    def __fetch_bank_id(self, bank_name: str) -> int | bool:
        """
        Fetch bank ID from bank name.

        Args:
            bank_name (str): The bank name.

        Returns:
            int | bool: Returns the bank ID if it exists, otherwise False.
        """
        ...

    def add_bank(self, bank_name: str) -> bool:
        """
        Add a bank name to the banks table.

        Args:
            bank_name (str): The bank name.

        Returns:
            bool: True if added, False otherwise.
        """
        ...

    def make_transaction(
        self, bank_name: str, amount: float, description: str | None = None
    ) -> bool:
        """
        Make a transaction for a bank.

        Args:
            bank_name (str): The bank name.
            amount (float): The amount of the transaction.
            description (str | None, optional): Optional description.

        Returns:
            bool: True if transaction succeeded, otherwise False.
        """
        ...
