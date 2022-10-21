#!/bin/sh
source /root/seng474/SENG474-Project/env/bin
cd /root/seng474/SENG474-Project/data_collection
python3 dotamatchretriever.py > /root/seng474/SENG474-Project/cron-errors.txt

