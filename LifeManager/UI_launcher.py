import os
import socket
import subprocess
from typing import Optional

from dotenv import load_dotenv


class UILauncher:
    def __init__(self, port: Optional[int] = None):

        if self.is_port_in_use(8569 if port is None else port):
            raise OSError(f"Port {port} is already in use")

        self.port = str(port)

    load_dotenv()

    def start(self):
        # Add project root to PYTHONPATH
        project_root = os.path.dirname(__file__)

        env = os.environ.copy()
        env["PYTHONPATH"] = project_root + os.pathsep + env.get("PYTHONPATH", "")

        # Path to the streamlit entry point
        module_path = os.path.join(project_root, "LocalUI", "main.py")
        # Run streamlit with modified env

        print("Checking to see if UI is running or no...")

        if self.process:
            print(f"Process is Already running at 'localhost:{self.port}'")
            return True
        else:
            try:
                self.process = subprocess.Popen(
                    ["streamlit", "run", module_path, "--server.port", self.port],
                    env=env,
                )
                return True

            except:
                print("An Error Occurred while starting the UI...")
                return False

    def stop(self):
        pass

    @staticmethod
    def is_port_in_use(port, host="127.0.0.1"):
        """True if port in use"""

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(1)  # Optional timeout
            try:
                s.bind((host, port))
                return False  # Port is free
            except OSError:
                return True  # Port is in use
