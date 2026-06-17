#!/usr/bin/env python3

import argparse
import os
'''
Ce script calcule la longueur des sequences homologue en utilisant le fichier d'alignement mafft
'''

def msa_lengths(input_file):
    seq_dict = {}

    with open(input_file, "r") as f:
        current_id = None
        current_seq = ""

        for line in f:
            line = line.strip()

            if line.startswith(">"):
                if current_id is not None:
                    clean_seq = current_seq.replace("-", "")
                    seq_dict[current_id] = len(clean_seq)

                current_id = line[1:]
                current_seq = ""
            else:
                current_seq += line

        # dernière séquence
        if current_id is not None:
            clean_seq = current_seq.replace("-", "")
            seq_dict[current_id] = len(clean_seq)

    return seq_dict


def main():
    parser = argparse.ArgumentParser(
        description="Compute sequence lengths from MSA files (ignoring gaps '-')"
    )

    parser.add_argument(
        "files",
        nargs="+",
        help="Input MSA files (FASTA format with gaps)"
    )

    args = parser.parse_args()

    for input_file in args.files:
        base = os.path.basename(input_file)
        prefix = os.path.splitext(base)[0]

        output_file = f"{prefix}_lengths.txt"

        seq_dict = msa_lengths(input_file)

        with open(output_file, "w") as out:
            for seq_id, length in seq_dict.items():
                out.write(f"{seq_id},{length}\n")

        print(f"{input_file} -> {output_file}")


if __name__ == "__main__":
    main()