#!/usr/bin/env python3
"""
Script pour renormmer dans le fichier dalignement (mafft ou fst) des homologue les nom de mes sequence ayant servir a construire mon profil hmm

USAGE : script.py \
    -i alignement.fst \
    -c alignement_hmm.fst \ # fichier ld'alignement ayant servir de construit le hmm profil
    -k tradd_SEED
"""
import argparse
import os


def get_unique_id(name):
    """
    Extrait : GCA_xxx|PROTEIN_ID depuis un header FASTA
    """
    parts = name.split("|")
    if len(parts) < 3:
        return None
    genome = parts[1]
    protein = parts[2].split("~")[0]
    return genome + "|" + protein


def get_keys_uniq(mafft_file_profil):
    """
    Récupère les IDs présents dans le fichier filtré
    """
    key_uniq = set()  # set = plus rapide

    with open(mafft_file_profil, "r") as file:
        for line in file:
            line = line.strip()
            if line.startswith(">"):
                key = get_unique_id(line)
                if key:
                    key_uniq.add(key)

    return key_uniq


def replace_keyword(mafft_file, keyword, key_uniq):
    base = os.path.basename(mafft_file)
    prefix = os.path.splitext(base)[0]
    output_file = f"{prefix}_{keyword}.MAFFT"

    with open(mafft_file, "r") as f, open(output_file, "w") as out:
        for line in f:
            if line.startswith(">"):
                line = line.strip()
                key = get_unique_id(line)

                # MODIFIER SEULEMENT SI présent dans key_uniq
                if key in key_uniq:
                    if "$" in line:
                        new_header = line.split("$")[0] + f"${keyword}"
                    else:
                        new_header = line + f"${keyword}"
                else:
                    # garder tel quel
                    new_header = line

                out.write(new_header + "\n")
            else:
                out.write(line)

    print(f"[OK] {mafft_file} -> {output_file}")


def main():
    parser = argparse.ArgumentParser(
        description="Replace keyword ONLY for selected sequences"
    )

    parser.add_argument("-i", "--input", required=True, help="homologue alignment file")
    parser.add_argument("-c", "--cut", required=True, help="Filtered FASTA file")
    parser.add_argument("-k", "--keyword", required=True, help="Keyword")

    args = parser.parse_args()

    key_uniq = get_keys_uniq(args.cut)

    replace_keyword(args.input, args.keyword, key_uniq)


if __name__ == "__main__":
    main()