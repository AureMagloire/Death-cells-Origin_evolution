#!/usr/bin/env python3
import argparse
import subprocess
import os

parser = argparse.ArgumentParser(description="Run FastTree on multiple protein alignments")
parser.add_argument("-f", "--files", nargs="+", required=True, help="Alignment files (FASTA)")
args = parser.parse_args()

for file in args.files:

    base = os.path.basename(file)
    name = os.path.splitext(base)[0]

    output_tree = os.path.join(".", name + ".tree")

    cmd = [
        "FastTree",
        "-cat", "20",
        "-gamma",
        "-lg",
        "-slow",
        file
    ]

    print(f"Running FastTree on {file}...")

    with open(output_tree, "w") as out:
        result = subprocess.run(cmd, stdout=out, stderr=subprocess.PIPE, text=True)

    if result.returncode == 0:
        print(f"Tree saved in {output_tree}")
    else:
        print(f"ERROR with {file}")
        print(result.stderr)