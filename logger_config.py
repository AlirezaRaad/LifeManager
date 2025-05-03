# logger_config.py
import datetime as dt
import logging
import os

# Ensure the log directory exists
os.makedirs("log", exist_ok=True)

# Create the logger
logger = logging.getLogger("shared_logger")
logger.setLevel(logging.DEBUG)

# Prevent adding handlers multiple times
if not logger.handlers:
    # Create a file handler with dynamic timestamp in the filename
    handler = logging.FileHandler(
        f"log/{dt.datetime.now().strftime('%d-%m-%Y--%H-%M-%S')}.log"
    )
    handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
    logger.addHandler(handler)
