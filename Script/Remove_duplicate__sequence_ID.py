#!/usr/bin/env python3

import argparse


def get_keys_uniq(name):
    parts = name.split("|")
    if len(parts) < 3:
        return None
    genome = parts[1]
    protein = parts[2].split("~")[0]
    return genome + "|" + protein


def extract_id_in_prec_file(prec_file):
    keys = set()

    with open(prec_file) as seed:
        for line in seed:
            if line.startswith(">"):
                name = line.strip()
                key = get_keys_uniq(name)
                if key is not None:
                    keys.add(key)
    print (len(keys))
    return keys


def remove_duplicate_sequences(input_fasta, output_fasta, keys):

    seen_keys = set()
    duplicated_count = 0
    seq_remove = set()

    with open(input_fasta) as fin, open(output_fasta, "w") as fout:

        write_sequence = False

        for line in fin:

            if line.startswith(">"):

                header = line.strip()
                cle = get_keys_uniq(header)

                # invalid key
                if cle is None:
                    write_sequence = False
                    continue

                # duplicate or in seed
                if cle in seen_keys or cle in keys:
                    duplicated_count += 1
                    seq_remove.add(header)
                    write_sequence = False

                else:
                    seen_keys.add(cle)
                    write_sequence = True
                    fout.write(line)

            else:
                if write_sequence:
                    fout.write(line)

    print(f"Nombre de séquences dupliquées supprimées : {duplicated_count}")
    print(f"Nombre de séquences uniques conservées : {len(seen_keys)}")


def main():

    parser = argparse.ArgumentParser(
        description="Remove duplicated FASTA entries based on GCF|XP unique key"
    )

    parser.add_argument("-i", "--input", required=True)
    parser.add_argument("-f", "--prec_file", required=True)
    parser.add_argument("-o", "--output", required=True)

    args = parser.parse_args()

    seed_ids = extract_id_in_prec_file(args.prec_file)

    remove_duplicate_sequences(
        args.input,
        args.output,
        seed_ids
    )


if __name__ == "__main__":
    main()