#!/usr/bin/env python3
import argparse
import subprocess
import os

'''
Script qui crée un profil Hmm a partir du fichier d'alignement nettoyé proprement
'''

parser = argparse.ArgumentParser(description="Run creat profil hmm on protein alignments")
parser.add_argument("-f", "--files", nargs="+", required=True, help="Alignment files (FST)")
args = parser.parse_args()

for file in args.files:

    base = os.path.basename(file)
    name = os.path.splitext(base)[0]

    prefix = name.split("_pp")[0]

    output_hmm = prefix + ".hmm"

    cmd = ["hmmbuild", output_hmm, file]

    print(f"Running creat hmm profil on {file}...")

    result = subprocess.run(cmd, stderr=subprocess.PIPE, text=True)

    if result.returncode == 0:
        print(f"Profil saved in {output_hmm}")
    else:
        print(f"ERROR with {file}")
        print(result.stderr)