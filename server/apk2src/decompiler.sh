#!/bin/bash

# Usage
if [ $# -ne 1 ]
then
	echo -e "Usage: $0 <apk filename>"
	exit 1
fi

# 1. Build JADX
if [ ! -f ./apk2src/jadx/build/jadx/bin/jadx ]; then
	./apk2src/jadx/gradlew dist -p ./apk2src/jadx/ > /dev/null 2>&1
fi

# 2. APK extraction
filename=$1
name="${filename%.*}"
./apk2src/jadx/build/jadx/bin/jadx --show-bad-code "$filename" -d "$name" > /dev/null #2>&1


