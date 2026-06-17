#!/usr/bin/env python3

'''
Script qui genere la longueur des sequence homology en utilisant le fichier fasta contenant les sequences homologues de la base de données
Usage : python script.py file1.fasta file2.fasta file3.fasta
'''

import sys
import os

def fasta_lengths(input_file):
    seq_dict = {}

    with open(input_file, "r") as f:
        current_id = None
        current_seq = ""

        for line in f:
            line = line.strip()

            if line.startswith(">"):
                if current_id is not None:
                    seq_dict[current_id] = len(current_seq)

                current_id = line[1:]  # enlever ">"
                current_seq = ""
            else:
                current_seq += line

        # dernière séquence
        if current_id is not None:
            seq_dict[current_id] = len(current_seq)
    #print(seq_dict)
    return seq_dict


def main():
    if len(sys.argv) < 2:
        print("Usage: python script.py file1.fasta file2.fasta ...")
        sys.exit(1)

    for input_file in sys.argv[1:]:
        # récupérer le nom sans extension
        base = os.path.basename(input_file)
        prefix = os.path.splitext(base)[0]

        output_file = f"{prefix}_lengths.txt"

        seq_dict = fasta_lengths(input_file)

        with open(output_file, "w") as out:
            for seq_id, length in seq_dict.items():
                out.write(f"{seq_id},{length}\n")

        print(f" {input_file} -> {output_file}")


if __name__ == "__main__":
    main()