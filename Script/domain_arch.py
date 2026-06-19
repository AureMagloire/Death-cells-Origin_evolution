#!/usr/bin/env python3

import sys
import re


def normalize(domain):
    return re.sub(r'_\d+$', '', domain)


def load_reference(ref_file):

    line = open(ref_file).readline().strip()
    arch = line.split("$")[1]

    return set(normalize(d) for d in arch.split("#"))


def main(input_file, ref_file, output_file):

    ref_domains = load_reference(ref_file)

    print("[INFO] Reference domains:", ref_domains)

    proteins = {}

    with open(input_file) as f:
        for line in f:

            line = line.strip()
            if not line:
                continue

            if "$" not in line:
                continue

            # ----------------------------
            # ID = EXACTEMENT le champ avant la virgule finale
            # MAIS SANS longueur
            # ----------------------------

            full = line.split(",")[0]

            # enlever uniquement ",1234" à la fin
            prot = full

            # ----------------------------
            # domains
            # ----------------------------
            arch = line.split("$")[1].split(",")[0]

            doms = {normalize(d) for d in arch.split("#")}

            proteins[prot] = doms

    # ----------------------------
    # selection
    # ----------------------------
    colored = []

    for prot, doms in proteins.items():

        if ref_domains.issubset(doms):
            colored.append(prot)

    # ----------------------------
    # iTOL output
    # ----------------------------
    with open(output_file, "w") as out:

        out.write("DATASET_COLORSTRIP\n")
        out.write("SEPARATOR TAB\n")
        out.write("DATASET_LABEL\tArchitecture\n")
        out.write("COLOR\t#FF0000\n\n")
        out.write("DATA\n")

        for prot in colored:
            out.write(f"{prot}\t#FF0000\n")

    print(f"[INFO] Proteins colored: {len(colored)}")


if __name__ == "__main__":

    if len(sys.argv) != 4:
        print("Usage: python domain_arch.py <input.txt> <ref.txt> <output.txt>")
        sys.exit(1)

    main(sys.argv[1], sys.argv[2], sys.argv[3])
