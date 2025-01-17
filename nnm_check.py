import os.path
import subprocess

if os.stat("error.log").st_size != 0:
    subprocess.call("./start.sh")
