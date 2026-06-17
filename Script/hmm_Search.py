#!/usr/bin/env python3
import argparse
import subprocess
import os

parser = argparse.ArgumentParser(
    description="Run hmmsearch on database using HMM profiles"
)

parser.add_argument(
    "-f", "--files", nargs="+", required=True,
    help="HMM profile files"
)

parser.add_argument(
    "-db", "--database", required=True,
    help="Protein database (FASTA)"
)

args = parser.parse_args()

database = args.database 

for file in args.files:

    base = os.path.basename(file)
    name = os.path.splitext(base)[0]

    prefix = name.replace("_hmm", "")
    output_hmms = prefix + "_table.hmms"

    cmd = ["hmmsearch","--noali", "--tblout", output_hmms, file, database]

    print(f"Searching homology for {file}...")

    result = subprocess.run(cmd, stderr=subprocess.PIPE, text=True)

    if result.returncode == 0:
        print(f"Results saved in {output_hmms}")
    else:
        print(f"ERROR with {file}")
        print(result.stderr)