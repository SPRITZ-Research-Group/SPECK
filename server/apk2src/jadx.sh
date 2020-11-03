#!/bin/bash

file=$1
name=$2
./apk2src/jadx/build/jadx/bin/jadx --show-bad-code -d $name $file
