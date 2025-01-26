import os.path
import subprocess
import sys

if os.stat("error.log").st_size != 0:
    subprocess.call("./start.sh")
    sys.exit(0)
