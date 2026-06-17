#!/usr/bin/env python3

from collections import defaultdict
import sys


# --------------------------------------------------
# 1. Load protein lengths + headers
# --------------------------------------------------
def load_lengths(length_file):

    lengths = {}
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

            lengths[prot_id] = length
            headers[prot_id] = header

    return lengths, headers


# --------------------------------------------------
# 2. Load HMMER domains
# --------------------------------------------------
def load_domains(tsv_file):
    """
    Construire la liste des domaines HMMER par protéine.

    Entré (tsv) : Protein_ID   domain   start   end ...

    sortie : domains[prot_id] = [(domain, start, end), ...]
    """

    domains = defaultdict(list)

    with open(tsv_file) as f:

        next(f)

        for line in f:

            if not line.strip():
                continue

            parts = line.rstrip().split("\t")

            raw_id = parts[0]

            # FIX ID CONSISTENCY
            clean_id = raw_id.split("~")[0]
            clean_id = clean_id.split("$")[0]
            prot_id = "|".join(clean_id.split("|")[-2:])

            domain = parts[1]
            start = parts[4]
            end = parts[5]

            domains[prot_id].append((domain, start, end))

    return domains


# --------------------------------------------------
# 3. Domain styles
# --------------------------------------------------
def build_domain_styles(domains):
    """
Créer une “palette visuelle” pour iTOL.
Il Récupère tous les types de domaines par leur nom et 2. Associe automatiquement une forme et une couleur a cahque type de domaine 
    """  

    all_domains = set()

    for dom_list in domains.values():
        for dom, _, _ in dom_list:
            all_domains.add(dom)

    all_domains = sorted(all_domains)

    shapes = [
        "RE", "EL", "DI", "TR", "TL", "OC",
        "HH", "HV", "PL", "PR", "PU", "PD"
    ]

    colors = [
        "#e41a1c", "#377eb8", "#4daf4a", "#984ea3",
        "#ff7f00", "#ffff33", "#a65628", "#f781bf",
        "#999999", "#66c2a5", "#fc8d62", "#8da0cb"
    ]

    styles = {}

    for i, domain in enumerate(all_domains):
        styles[domain] = (
            shapes[i % len(shapes)],
            colors[i % len(colors)]
        )

    return styles


# --------------------------------------------------
# 4. Write iTOL dataset
# --------------------------------------------------
def write_itol(domains, lengths, headers, output_file):
    """
    Construire le fichier final iTOL
    """

    domain_styles = build_domain_styles(domains)

    legend_shapes = []
    legend_colors = []
    legend_labels = []

    for domain in sorted(domain_styles):
        shape, color = domain_styles[domain]
        legend_shapes.append(shape)
        legend_colors.append(color)
        legend_labels.append(domain)

    with open(output_file, "w") as out:

        out.write("DATASET_DOMAINS\n")
        out.write("SEPARATOR COMMA\n")
        out.write("DATASET_LABEL,Protein_domains\n")
        out.write("LEGEND_TITLE,Protein domains\n")
        out.write("COLOR,#ff0000\n")

        out.write("LEGEND_SHAPES," + ",".join(legend_shapes) + "\n")
        out.write("LEGEND_COLORS," + ",".join(legend_colors) + "\n")
        out.write("LEGEND_LABELS," + ",".join(legend_labels) + "\n")

        out.write("DATA\n")

        written = 0

        # ✅ IMPORTANT: loop on ALL proteins (not only domains)
        for prot_id, length in lengths.items():

            if prot_id not in headers:
                continue

            tree_header = headers[prot_id]

            # ---------------------------
            # CASE 1: no domains
            # ---------------------------
            if prot_id not in domains:

                row = [
                    tree_header,
                    length,
                    f"RE|1|{length}|#bdbdbd|no_domain"
                ]

                out.write(",".join(row) + "\n")
                written += 1
                continue

            # ---------------------------
            # CASE 2: domains exist
            # ---------------------------
            dom_list = domains[prot_id]

            row = [tree_header, length]

            for dom, start, end in dom_list:

                shape, color = domain_styles[dom]

                row.append(
                    f"{shape}|{start}|{end}|{color}|{dom}"
                )

            out.write(",".join(row) + "\n")
            written += 1

    print(f"[INFO] Proteins written in iTOL file: {written}")


# --------------------------------------------------
# 5. MAIN
# --------------------------------------------------
def main(tsv_file, length_file, output_file):

    domains = load_domains(tsv_file)
    lengths, headers = load_lengths(length_file)

    print(f"[DEBUG] domains proteins: {len(domains)}")
    print(f"[DEBUG] lengths proteins: {len(lengths)}")

    print("[DEBUG] example domain ID:", next(iter(domains)))
    print("[DEBUG] example length ID:", next(iter(lengths)))

    write_itol(domains, lengths, headers, output_file)


# --------------------------------------------------
# 6. RUN
# --------------------------------------------------
if __name__ == "__main__":

    if len(sys.argv) != 4:
        print("Usage: Itol_domain.py domains.tsv lengths.txt output.txt")
        sys.exit(1)

    main(sys.argv[1], sys.argv[2], sys.argv[3])