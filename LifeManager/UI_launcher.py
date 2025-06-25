import os
import signal
import subprocess
from typing import Optional

import psutil
from dotenv import load_dotenv


class UILauncher:
    def __init__(self):

        self.port = "8569"
        self.process = None

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
            print(f"Process is Already running at http://localhost:{self.port}")
            return True
        else:
            try:
                self.process = subprocess.Popen(
                    ["streamlit", "run", module_path, "--server.port", str(self.port)],
                    env=env,
                )
                return True

            except:
                print("An Error Occurred while starting the UI...")
                return False

    def stop(self):
        if self.process:
            print(f"Stopping the UI running at 'localhost:{self.port}'...")
            try:
                # Terminate the subprocess
                self.process.terminate()
                self.process.wait(timeout=5)
                self.process = None
                print("UI successfully stopped.")
                return True

            except subprocess.TimeoutExpired:
                print("Graceful shutdown failed, forcing termination...")
                self.process.kill()
                self.process.wait()
                self.process = None
                return True

            except Exception as e:
                print(f"Error while stopping the UI: {e}")
                return False
        else:
            print("No UI process is currently running.")
            return False

    def kill_port_8569(self, force: bool = True) -> bool:

        pid = self.__find_pid_using_port(self.port)
        if pid:
            # print(f"Port {self.port} is in use by PID {pid}")
            if self.__kill_process(pid, force):
                print(f"Successfully killed process {pid}")
                return True
            else:
                print(f"Failed to kill process {pid}")
                return False
        else:
            print(f"Port {self.port} is already free")
            return False

    @staticmethod
    def __kill_process(pid: int, force: bool = False) -> bool:
        """
        Kills the process with the given PID.
        If force=True, sends SIGKILL (Unix only), otherwise SIGTERM.
        """
        try:
            sig = (
                signal.SIGKILL
                if force and hasattr(signal, "SIGKILL")
                else signal.SIGTERM
            )
            os.kill(pid, sig)
            return True
        except Exception as e:
            print(f"Failed to kill PID {pid}: {e}")
            return False

    @staticmethod
    def __find_pid_using_port(port: int) -> int | None:
        """
        Returns the PID of the process using the given port, or None if free.
        """

        for conn in psutil.net_connections(kind="inet"):
            if conn.laddr and conn.laddr.port == port and conn.pid:
                return conn.pid
        return None
