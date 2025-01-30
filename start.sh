#!/bin/sh

echo "Stop the script"
while pgrep -f "nnm_main.py" > /dev/null; do
    pkill -f -n nnm_main.py
    sleep 1
done

echo "Copy current log files"
date=$(date +"%Y-%m-%d %T")
cp error.log logs/error_"$date".log
cp output.log logs/output_"$date".log

echo "Delete Empty Files"
find logs/ -type f -empty ! -name ".gitignore" -print -delete

echo "Delete log files older than 7 days"
find logs/ -type f -mtime +7 -print -delete

sleep 3

echo "Start the script"
nohup .venv/bin/python nnm_main.py> output.log  2> error.log & echo $! > bot.pid