#!/usr/bin/env python3
"""
Script pour renormmer le nom de mes sequence ayant servir a construire mon profil hmm. Cela me permettra de retrouver ces sequence dans larbre garce au mot clé SEED que j'ai ajouté au noms des seq
"""
import argparse
import os


def replace_keyword(input_file, keyword):
    base = os.path.basename(input_file)
    prefix = os.path.splitext(base)[0]
    output_file = f"{prefix}_{keyword}.fst"

    with open(input_file, "r") as f, open(output_file, "w") as out:
        for line in f:
            if line.startswith(">"):
                line = line.strip()

                if "$" in line:
                    # garder tout avant $
                    new_header = line.split("$")[0] + f"${keyword}"
                else:
                    # si pas de $, on ajoute juste
                    new_header = line + f"${keyword}"

                out.write(new_header + "\n")
            else:
                out.write(line)

    print(f"[OK] {input_file} -> {output_file}")


def main():
    parser = argparse.ArgumentParser(
        description="Replace annotation after '$' in FASTA headers with a keyword"
    )

    parser.add_argument("file", help="Input FASTA file")
    parser.add_argument("keyword", help="Keyword to insert after '$'")

    args = parser.parse_args()

    replace_keyword(args.file, args.keyword)


if __name__ == "__main__":
    main()