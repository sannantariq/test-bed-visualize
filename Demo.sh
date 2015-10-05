#!/bin/bash

python Collect_Server.py &
sleep 2
./run_eddies.sh &
python Streamer.py
