#!/usr/bin/env python3

from collections import defaultdict
import re
import sys


# --------------------------------------------------
# 1. Load protein headers
# --------------------------------------------------
def load_headers(length_file):

    headers = {}

    with open(length_file) as f:

        for line in f:

            line = line.strip()

            if not line:
                continue

            header, length = line.split(",")

            clean_header = header.split("~")[0]
            clean_header = clean_header.split("$")[0]

            prot_id = "|".join(clean_header.split("|")[-2:])

            headers[prot_id] = header

    return headers


# --------------------------------------------------
# 2. Load HMMER domains
# --------------------------------------------------
def load_domains(tsv_file):

    domains = defaultdict(list)

    with open(tsv_file) as f:

        next(f)

        for line in f:

            if not line.strip():
                continue

            parts = line.rstrip().split("\t")

            raw_id = parts[0]

            clean_id = raw_id.split("~")[0]
            clean_id = clean_id.split("$")[0]

            prot_id = "|".join(clean_id.split("|")[-2:])

            domain = parts[1]

            start = int(parts[4])
            end = int(parts[5])

            domains[prot_id].append(
                (domain, start, end)
            )

    return domains


# --------------------------------------------------
# 3. Normalize domain names
# --------------------------------------------------
def normalize_domain(domain):
    """
    Ank_14 -> Ank
    Ank_2 -> Ank
    CARDM_3 -> CARDM
    """

    return re.sub(r'_\d+$', '', domain)


# --------------------------------------------------
# 4. Build protein architecture
# --------------------------------------------------
def get_protein_architecture(dom_list):

    dom_list = sorted(
        dom_list,
        key=lambda x: x[1]
    )

    architecture = []

    for dom, start, end in dom_list:

        architecture.append(
            normalize_domain(dom)
        )

    return architecture


# --------------------------------------------------
# 5. Collapse consecutive repeats
# --------------------------------------------------
def collapse_repeats(domain_list):

    collapsed = []

    for dom in domain_list:

        if not collapsed:
            collapsed.append(dom)

        elif dom != collapsed[-1]:
            collapsed.append(dom)

    return collapsed


# --------------------------------------------------
# 6. Compare architectures
# --------------------------------------------------
def architecture_match(observed, expected):

    observed = collapse_repeats(observed)
    expected = collapse_repeats(expected)

    return observed == expected


# --------------------------------------------------
# 7. Load architectures of interest
# --------------------------------------------------
def load_architectures(arch_file):

    architectures = {}

    with open(arch_file) as f:

        for line in f:

            line = line.strip()

            if not line:
                continue

            architecture, label = line.split()

            architectures[label] = [
                normalize_domain(x)
                for x in architecture.split("#")
            ]

    return architectures


# --------------------------------------------------
# 8. Assign colors
# --------------------------------------------------
def build_architecture_colors(architectures):

    colors = [
        "#e41a1c",
        "#377eb8",
        "#4daf4a",
        "#984ea3",
        "#ff7f00",
        "#ffff33",
        "#a65628",
        "#f781bf",
        "#999999",
        "#66c2a5",
        "#fc8d62",
        "#8da0cb"
    ]

    arch_colors = {}

    for i, label in enumerate(sorted(architectures)):

        arch_colors[label] = colors[
            i % len(colors)
        ]

    return arch_colors


# --------------------------------------------------
# 9. Find matching architecture
# --------------------------------------------------
def find_architecture(dom_list, architectures):

    observed = get_protein_architecture(dom_list)

    for label, expected in architectures.items():

        if architecture_match(
            observed,
            expected
        ):
            return label

    return None


# --------------------------------------------------
# 10. Write TREE_COLORS dataset
# --------------------------------------------------
def write_tree_colors(
    domains,
    headers,
    architectures,
    output_file
):

    arch_colors = build_architecture_colors(
        architectures
    )

    written = 0

    with open(output_file, "w") as out:

        out.write("TREE_COLORS\n")
        out.write("SEPARATOR TAB\n")
        out.write("DATA\n")

        for prot_id, dom_list in domains.items():

            if prot_id not in headers:
                continue

            label = find_architecture(
                dom_list,
                architectures
            )

            if label is None:
                continue

            color = arch_colors[label]

            out.write(
                f"{headers[prot_id]}\tbranch\t{color}\tnormal\n"
            )

            written += 1

    print(
        f"[INFO] Colored proteins: {written}"
    )


# --------------------------------------------------
# MAIN
# --------------------------------------------------
def main(
    domains_file,
    lengths_file,
    architecture_file,
    output_file
):

    domains = load_domains(
        domains_file
    )

    headers = load_headers(
        lengths_file
    )

    architectures = load_architectures(
        architecture_file
    )

    print(
        f"[INFO] Proteins with domains: {len(domains)}"
    )

    print(
        f"[INFO] Architectures loaded: {len(architectures)}"
    )

    write_tree_colors(
        domains,
        headers,
        architectures,
        output_file
    )


# --------------------------------------------------
# RUN
# --------------------------------------------------
if __name__ == "__main__":

    if len(sys.argv) != 5:

        print(
            "Usage: python Itol_architecture_colors.py "
            "domains.tsv lengths.txt architectures.txt output.txt"
        )

        sys.exit(1)

    main(
        sys.argv[1],
        sys.argv[2],
        sys.argv[3],
        sys.argv[4]
    )