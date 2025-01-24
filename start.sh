#!/bin/sh

echo "Stop the script"
pkill -f -n nnm_main.py
pkill -f -n nnm_main.py
pkill -f -n nnm_main.py
pkill -f -n nnm_main.py

sleep 3

echo "Copy current log files"
date=$(date +"%Y-%m-%d %T")
cp error.log logs/error_"$date".log
cp output.log logs/output_"$date".log

echo "Delete Empty Files"
find logs/ -type f -empty -print -delete

sleep 3

echo "Start the script"
nohup .venv/bin/python nnm_main.py> output.log  2> error.log & echo $! > bot.pid