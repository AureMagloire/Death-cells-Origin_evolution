#!/usr/bin/env python3

import argparse
from operator import pos
import subprocess
import os


def run_blastp(file,database,table=False):
    query = file
    database = database
    prefix = os.path.splitext(os.path.basename(query))[0] 
    outfile = f"{prefix}.tab_blastp"

    if table: 
        cmd = f'blastp -db {database} -query {query} -max_target_seqs 1000 -outfmt "7 qacc sacc evalue qcovs nident gaps" -evalue 1E-10 -out {outfile}'

    else :
        cmd = f"blastp -db {database} -query {query} -num_descriptions 1000 -num_alignments 1000 -evalue 1E-10 -out {outfile}"

    if os.path.exists(query):
        print(f"{prefix}")
    else:
        print("Could not open query file")
        return None 

    if os.path.exists(outfile):
        print(f"...blastp for {prefix} already done")
        return outfile 
    else:
        print(f".....runing blastp for {prefix}")
        subprocess.run(cmd, shell =True, text = True)
        return outfile


def main() : 
    parser = argparse.ArgumentParser(description="homology reseache whith blastp")

    parser.add_argument("-f", "--files", nargs="+", required=True, help="List of protein sequence file")

    parser.add_argument("-db", "--database", required=True, help="database")

    parser.add_argument("-t", "--table", action="store_true", help="output blastp results in csv format" )
    
    args = parser.parse_args()
    for file in args.files : 
        blastp_file = run_blastp(file, args.database,args.table)
        if blastp_file:
            print(f"the best hits stored in {blastp_file}")
        else:
            print(f"blastp failed for {file}")
if __name__ == "__main__":
    main()