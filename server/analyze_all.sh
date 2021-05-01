#!/bin/bash

download_path="../download/"

for i in `ls $download_path`; do
  echo "$i"
  echo "*********************************************************"
  # echo "$download_path$i"
  # echo "$1"
  python3 Scan.py -s $download_path/$i -r $1 -D SPECK_data_rule$1 -f -p ~/Android/Sdk
  echo "*********************************************************"

done;
