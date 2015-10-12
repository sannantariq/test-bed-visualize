#!/bin/bash
sleep 5
python Collect_Server.py &
sleep 5
./run_eddies.sh &
gnome-terminal -e ./Streamer.py
