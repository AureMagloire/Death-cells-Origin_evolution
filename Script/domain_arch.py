#!/usr/bin/env python3

from collections import OrderedDict
import re
import sys


def normalize_domain(domain):
    # supprime les suffixes type _1, _2, etc.
    return re.sub(r'_\d+$', '', domain)


def collapse_repeats(domains):
    # enlève les répétitions consécutives uniquement
    collapsed = []
    for dom in domains:
        if not collapsed or dom != collapsed[-1]:
            collapsed.append(dom)
    return collapsed


def main(input_file, output_file):

    architectures = OrderedDict()

    try:
        with open(input_file) as f:
            for line in f:

                line = line.strip()
                if not line:
                    continue

                # prend la partie avant la première virgule
                header = line.split(",")[0]

                # on ne garde que les lignes contenant $
                if "$" not in header:
                    continue

                arch = header.split("$")[-1]

                domains = [
                    normalize_domain(x)
                    for x in arch.split("#")
                    if x != ""
                ]

                domains = collapse_repeats(domains)

                normalized_arch = "#".join(domains)

                if normalized_arch not in architectures:
                    architectures[normalized_arch] = normalized_arch.replace("#", "_")

    except FileNotFoundError:
        print(f"ERROR: input file not found -> {input_file}")
        sys.exit(1)

    with open(output_file, "w") as out:
        for arch, label in architectures.items():
            out.write(f"{arch} {label}\n")

    print(f"{len(architectures)} unique architectures written to {output_file}")


if __name__ == "__main__":

    if len(sys.argv) != 3:
        print("Usage: python domain_arch.py <input_file> <output_file>")
        sys.exit(1)

    main(sys.argv[1], sys.argv[2])
