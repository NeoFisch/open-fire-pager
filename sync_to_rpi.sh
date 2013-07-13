#!/bin/bash


echo "========================= Starting PUSH to Raspberry PI  =========================="
rsync --stats --delete -auvze 'ssh' /Users/manuel/Projects/open-fire-pager/src/ pi:/home/manuel/open-fire-pager/
echo "=========================== Sync to Raspberry PI done. ============================"