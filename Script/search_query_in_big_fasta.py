#!/usr/bin/env python3

import sys

big_fasta = sys.argv[1]
uniprot_fasta = sys.argv[2]
output_fasta = sys.argv[3]

"""
FASTA sequence matching (no external libraries)

Description:
This script compares two FASTA files (a large reference FASTA and a UniProt FASTA)
and extracts sequences that are exactly identical in both files.

It uses Python dictionaries for fast lookup:
- Key: amino acid sequence
- Value: FASTA header

Only exact sequence matches are reported.

Usage:
    python script.py big_fasta.fa uniprot.fasta output.txt

Output:
    A FASTA file containing sequences (header + sequence) from the big FASTA
    that are exactly found in the UniProt FASTA.
"""

def read_fasta_to_dict(path):
    fasta_dict = {}
    header = None
    seq_lines = []

    with open(path, "r") as f:
        for line in f:
            line = line.strip()

            if not line:
                continue

            if line.startswith(">"):
                if header is not None:
                    seq = "".join(seq_lines)
                    fasta_dict[seq] = header

                header = line.strip(">")
                seq_lines = []
            else:
                seq_lines.append(line)

        # dernier record
        if header is not None:
            seq = "".join(seq_lines)
            fasta_dict[seq] = header

    return fasta_dict


# dictionnaires
big_dict = read_fasta_to_dict(big_fasta)
uniprot_dict = read_fasta_to_dict(uniprot_fasta)

# recherche des correspondances
matches = []

for seq in uniprot_dict.keys():
    if seq in big_dict:
        header = big_dict[seq]

        # écrire format FASTA original (le header seul)
        matches.append(header)


# output
with open(output_fasta, "w") as out:
    out.write("\n".join(matches) + "\n")

print(f"{len(matches)} séquence(s) identique(s) trouvée(s)")