import os
from sys import argv
import subprocess

PATH = argv[1]

apks = [a for a in os.listdir(PATH) if a.endswith(".apk")]

for apk in apks:
    output_dir = f"{PATH}/{apk}"[:-4]
    subprocess.run(["jadx", f"{PATH}/{apk}", "-d", output_dir])