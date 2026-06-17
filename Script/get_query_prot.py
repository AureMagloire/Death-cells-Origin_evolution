#!/usr/bin/env python3

import argparse
import subprocess

def get_accession(gene, organism):
    query = f"{gene}[Gene] AND {organism}[Organism]"
    cmd = f'esearch -db protein -query "{query}" | efetch -format acc'

    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    accessions = result.stdout.strip().split("\n")
    if accessions:
        print(accessions)
        return accessions[0]
    else:
        return None

def fetch_fasta(acc, gene, org_code):
    outfile = f"{gene}_{org_code}.prt"
    cmd = f"efetch -db protein -id {acc} -format fasta"

    with open(outfile, "w") as f:
        subprocess.run(cmd.split(), stdout=f)

def main():
    parser = argparse.ArgumentParser(description="Download protein sequences from NCBI")

    parser.add_argument("-g", "--genes", nargs="+", required=True,
                        help="List of gene names")

    parser.add_argument("-o", "--organism", required=True,
                        help="Organism name (e.g. 'Homo sapiens')")

    parser.add_argument("-c", "--code", required=True,
                        help="Short organism code for outfile(e.g. hs for homo sapiens)")

    args = parser.parse_args()

    for gene in args.genes:
        acc = get_accession(gene, args.organism)

        if acc:
            print(f"Downloading {gene} ({acc})")
            fetch_fasta(acc, gene, args.code)
        else:
            print(f"No accession found for {gene}")

if __name__ == "__main__":
    main()
