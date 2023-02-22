#!/usr/bin/python3

import sys, os, subprocess

apk2src_path = os.path.dirname(os.path.realpath(__file__))      # this is the current running path

jadx_path = apk2src_path + '/jadx'
bin_path = jadx_path + '/build/jadx/bin'

sys.path.insert(0, jadx_path)
sys.path.insert(0, bin_path)


apk_path = sys.argv[1]					# get the aph's absolute path from args
dir_name = apk_path[:-4]				# get the dir name when we put the decompiled app

if not os.path.isfile(f"{bin_path}/jadx"):											# if the bin 'jadx' doesn't exist...
	subprocess.run([f"jadx", apk_path, "-d", dir_name])						# try to see if it is installed in PATH
else :
	subprocess.run([f"{bin_path}/jadx", apk_path, "-d", dir_name])						# otherwise run from subdir