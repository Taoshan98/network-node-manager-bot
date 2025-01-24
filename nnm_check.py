import os.path
import subprocess

with open("bot.pid", "r", encoding="utf-8") as file:
    pid = int(file.readline().strip())

    try:
        os.kill(pid, 0)
    except (FileNotFoundError, ValueError) as e:
        subprocess.call("./start.sh")
        exit()

if os.stat("error.log").st_size != 0:
    subprocess.call("./start.sh")
    exit()
