import os
import subprocess

from dotenv import load_dotenv

load_dotenv()

# Add project root to PYTHONPATH
project_root = os.path.dirname(__file__)
env = os.environ.copy()
env["PYTHONPATH"] = project_root + os.pathsep + env.get("PYTHONPATH", "")

# Path to the streamlit entry point
module_path = os.path.join(project_root, "LocalUI", "main.py")

# Run streamlit with modified env
subprocess.run(["streamlit", "run", module_path, "--server.port", "8569"], env=env)
