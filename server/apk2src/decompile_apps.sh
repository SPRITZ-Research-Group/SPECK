#!/bin/bash

decompiler="./apk2src/jadx.sh"

apks=$1

files=`find ${apks} -name '*.apk'`

# replace spaces with _
srcDir=`pwd`
cd ${apks}
if [ "$(uname)" == "Darwin" ]; then
	for f in *\ *; do mv "$f" "${f// /_}" > /dev/null 2>&1; done # MAC OS
else
	find -name "* *" -type f | rename 's/ /_/g' # UBUNTU 16
fi

cd ${srcDir}
files=`find ${apks} -name '*.apk'`


nbFiles=0
nbErrors=0

start_time="$(date -u +%s)"

for file in $files
do
	name="${file%.*}"
	eval "$decompiler $file $name"
done

nbFiles=$(($nbFiles+`find . -name '*.java' | wc -l`))
nbErrors=$(($nbErrors+`grep -r -F "JADX" . | sort -u | wc -l`))

end_time="$(date -u +%s)"

elapsed="$(($end_time-$start_time))"

echo "[RESULTS]"
echo "[+] Total of $elapsed seconds elapsed for process"

echo "[=>] files  = ${nbFiles}"
echo "[=>] errors = ${nbErrors}"

