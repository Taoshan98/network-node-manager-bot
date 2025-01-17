#!/bin/sh

echo "Arresto il bot"
pkill -f -n nnm_main.py
pkill -f -n nnm_main.py
pkill -f -n nnm_main.py
pkill -f -n nnm_main.py

sleep 3

echo "Copio file di errore"
date=$(date +"%Y-%m-%d %T")
cp error.log logs/error_"$date".log
cp output.log logs/output_"$date".log

echo "Elimino File vuoti"
find logs/ -type f -empty -print -delete

sleep 3

echo "Avvio Bot"
nohup .venv/bin/python nnm_main.py> output.log  2> error.log & echo $! > bot.pid