#!/usr/bin/env python3

import argparse
import os

"""
Ce script extrait des séquences protéiques depuis la base de données FASTA
à partir d’identifiants issus soit d’un fichier de sortie hmmsearch (--tblout),
soit d’un fichier TSV contenant une liste d’IDs unique des meilleur hits.

- Mode HMMSEARCH (-f) : récupère les IDs depuis un fichier hmmsearch : script.py -f MLKL.hmms -db database.faa
- Mode TSV (-t)   : utilise directement une liste d’IDs (colonne ID) : script.py -t best_hits.tsv -db database.faa

Les séquences correspondantes sont ensuite extraites de la base de données
et écrites dans un fichier FASTA de sortie.
"""
# 🔹 extraction ID depuis header
def get_keys_uniq(name):
    parts = name.split("|")
    if len(parts) < 3:
        return None
    genome = parts[1]
    protein = parts[2].split("~")[0]
    return genome + "|" + protein


# 🔹 extraction depuis hmmsearch
def extract_ids_from_hmmers_file(hmmers_file):

    keys_uniq = set()

    with open(hmmers_file) as f:
        for line in f:
            if line.startswith("#") or line.strip() == "":
                continue

            fields = line.split()
            target = fields[0]

            extracted_id = get_keys_uniq(target)
            if extracted_id:
                keys_uniq.add(extracted_id)

    return keys_uniq


# 🔹 extraction depuis TSV
def extract_ids_from_tsv(tsv_file):

    keys_uniq = set()

    with open(tsv_file) as f:
        next(f)  # skip header

        for line in f:
            if line.strip() == "":
                continue

            fields = line.strip().split("\t")
            keys_uniq.add(fields[0])

    return keys_uniq


# 🔹 extraction des séquences
def extract_sequences(database, keys_uniq, output):

    write = False

    with open(database) as db, open(output, "w") as out:

        for line in db:

            if line.startswith(">"):
                header = line.split("=")[0]
                key = get_keys_uniq(header)

                if key in keys_uniq:
                    write = True
                    out.write(line)
                else:
                    write = False

            else:
                if write:
                    out.write(line)


def main():
    parser = argparse.ArgumentParser(
        description="Extract sequences from database using HMMER or TSV IDs"
    )

    group = parser.add_mutually_exclusive_group(required=True)

    group.add_argument("-f", "--hmmers_file", nargs="+",
                       help="hmmsearch output file(s)")

    group.add_argument("-t", "--tsv_file", nargs="+",
                       help="TSV file(s) with IDs")

    parser.add_argument("-db", "--database", required=True,
                        help="database FASTA")

    args = parser.parse_args()

    files = args.hmmers_file if args.hmmers_file else args.tsv_file

    for file in files:

        print(f"Traitement : {file}")

        # 🔹 choisir la source
        if args.hmmers_file:
            keys_uniq = extract_ids_from_hmmers_file(file)
        else:
            keys_uniq = extract_ids_from_tsv(file)

        prefix = os.path.splitext(os.path.basename(file))[0]
        output = f"{prefix}_homologues.faa"

        print(f"{len(keys_uniq)} sequences trouvées")
        print(f"Output : {output}")

        extract_sequences(args.database, keys_uniq, output)


if __name__ == "__main__":
    main()