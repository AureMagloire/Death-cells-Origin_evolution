#!/usr/bin/env python3
import argparse
import subprocess
from pathlib import Path
import sys

"""
Run HMMER hmmscan on a protein FASTA file against an HMM database
and automatically generate output files based on the input filename.

This script:
- Runs hmmscan with a user-defined number of CPU threads
- Uses a provided HMM database (e.g. Pfam)
- Takes a FASTA file containing one or multiple protein sequences
- Produces three output files:
    * <input>.hmmscan   : full hmmscan output
    * <input>.tblout    : per-sequence summary table
    * <input>.domtblout : per-domain hits table (most useful for analysis)

Requirements:
- HMMER installed (hmmscan available in PATH)
- HMM database already prepared with hmmpress (if needed)

Example usage:
    python Run_hmmScan.py -t 20 \
        --hmmdb Hmm_base/Pfam-A.hmm \
        -f RIPK3_hs.prt

Output:
    RIPK3_hs.hmmscan
    RIPK3_hs.tblout
    RIPK3_hs.domtblout
"""

def main():
    parser = argparse.ArgumentParser(
        description="Run hmmscan and generate output files based on the FASTA name."
    )

    parser.add_argument(
        "-t", "--cpu",
        type=int,
        required=True,
        help="Number of CPUs to use"
    )

    parser.add_argument(
        "--hmmdb",
        required=True,
        help="Path to HMM database"
    )

    parser.add_argument(
        "-f", "--fasta",
        required=True,
        help="Protein FASTA file"
    )

    args = parser.parse_args()

    fasta = Path(args.fasta)

    if not fasta.exists():
        sys.exit(f"ERROR: FASTA file not found: {fasta}")

    hmmdb = Path(args.hmmdb)

    if not hmmdb.exists():
        sys.exit(f"ERROR: HMM database not found: {hmmdb}")

    basename = fasta.stem

    domtblout = f"{basename}.domtblout"
    tblout = f"{basename}.tblout"
    hmmscan_out = f"{basename}.hmmscan"

    cmd = [
        "hmmscan",
        "--cpu", str(args.cpu),
        "--noali",
        "--domtblout", domtblout,
        "--tblout", tblout,
        str(hmmdb),
        str(fasta)
    ]

    print("Running:")
    print(" ".join(cmd))
    print()

    with open(hmmscan_out, "w") as out:
        subprocess.run(cmd, stdout=out, check=True)

    print("Finished successfully.")
    print(f"domtblout : {domtblout}")
    print(f"tblout    : {tblout}")
    print(f"hmmscan   : {hmmscan_out}")


if __name__ == "__main__":
    main()