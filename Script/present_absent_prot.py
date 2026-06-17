#!/usr/bin/env python3
import argparse
import pandas as pd
import os
import matplotlib.pyplot as plt


# ---------------------------
# 1. DATABASE PARSING
# ---------------------------
def extract_accessions(db_file):
    """
    Extract genome metadata from FASTA database.

    Returns:
        dict:
        {accession: {
            species: str,
            phylum: str,
            header: str   # important for iTOL matching
        }}
    """
    accessions = {}

    with open(db_file) as f:
        for line in f:
            if line.startswith(">"):

                header = line.strip()[1:]
                parts = header.split("|")

                acc = parts[1]
                species = parts[0]

                tax_info = parts[2].split("=")[-1]
                phylum = tax_info.split("-")[1]

                accessions[acc] = {
                    "species": species,
                    "phylum": phylum}

    print(f"{len(accessions)} genomes enregistrés")
    return accessions


# ---------------------------
# 2. ALIGNMENT COUNTING
# ---------------------------
def count_accessions_in_alignment(alignment_file, accessions):
    """
    Count occurrences of each accession in alignment.
    Also ensures mapping with correct header.
    """
    dico = {acc: 0 for acc in accessions}

    with open(alignment_file, "r") as f:
        for line in f:
            if line.startswith(">"):

                header = line.strip()[1:]
                parts = header.split("|")
                acc_match = parts[1]

                if acc_match in dico:
                    dico[acc_match] += 1

    return dico


# ---------------------------
# 3. GENE NAME
# ---------------------------
def get_gene_name(filename):
    """Extract gene name from filename."""
    base = os.path.basename(filename)
    return base.split("_")[0]





# ---------------------------
# 6. MAIN PIPELINE
# ---------------------------
def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("-db", "--database", required=True)
    parser.add_argument("-a", "--alignments", nargs="+", required=True)

    args = parser.parse_args()

    # 1. Load database
    accessions = extract_accessions(args.database)

    # 2. Build dataframe
    df = pd.DataFrame.from_dict(accessions, orient="index")
    df.index.name = "Accession"

    # 3. Add gene counts
    for aln_file in args.alignments:

        gene = get_gene_name(aln_file)
        counts = count_accessions_in_alignment(aln_file, accessions)

        df[gene] = pd.Series(counts)

    # 4. Clean
    df = df.fillna(0)
    df = df.sort_values(by=["phylum", "species"])

    # 5. Export results
    df.to_excel("Present_absence_gene.xlsx")

    print("Done ✔ Files generated:")
    print(" - Present_absence_gene.xlsx")
# ---------------------------
# ENTRY POINT
# ---------------------------
if __name__ == "__main__":
    main()