#!/bin/sh

echo "Stopping Bot..."
while pgrep -f "nnm_main.py" > /dev/null; do
    pkill -f -n nnm_main.py
    sleep 1
done

echo "Updating Sources..."
sleep 2

git checkout main > /dev/null 2>&1
git reset --hard HEAD > /dev/null 2>&1
git stash > /dev/null 2>&1
git clean -d -f . > /dev/null 2>&1
git pull > /dev/null 2>&1

echo "Restarting Bot..."
sleep 2

chmod +x start.sh
./start.sh