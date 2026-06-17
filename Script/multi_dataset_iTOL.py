#!/usr/bin/env python3

"""
SCRIPT COMPLET iTOL

Génère 3 fichiers :
1. DATASET_RANGE → phylum (clades colorés)
2. DATASET_BINARY → triangles
3. DATASET_SIMPLEBAR → longueurs protéines

USAGE : 
python multidataset_iTOL.py \
 -t arbre.treefile \
 -m markers.txt \
 -l lengths.txt \
 -o itol

IMPORTANT :
Chaque dataset iTOL = 1 fichier séparé et on a : 
itol_range.txt
itol_binary.txt
itol_bar.txt
"""

import re
from collections import defaultdict


# --------------------------------------------------
# 1. EXTRACTION PHYLUM
# --------------------------------------------------
def extract_phylum(label):
    """
    Récupère le phylum depuis le label IQ-TREE
    """
    try:
        return label.split("=Eukaryota-")[1].split("-")[0]
    except:
        return "Unknown"


# --------------------------------------------------
# 2. EXTRACTION FEUILLES
# --------------------------------------------------
def extract_leaves(newick):
    """
    Récupère uniquement les feuilles (taxa)
    et ignore bootstrap
    """
    tokens = re.split(r"[(),;]", newick)
    leaves = []

    for t in tokens:
        t = t.strip()
        if not t:
            continue

        t = t.split(":")[0]

        # ignorer bootstrap
        if re.match(r"^[0-9]+(\.[0-9]+)?(/[0-9]+(\.[0-9]+)?)?$", t):
            continue

        if "Eukaryota" in t:
            leaves.append(t)

    return leaves


# --------------------------------------------------
# 3. COULEURS
# --------------------------------------------------
def generate_colors(n):
    import colorsys
    colors = []

    for i in range(n):
        h = i / n
        rgb = colorsys.hsv_to_rgb(h, 0.6, 0.9)
        colors.append("#{:02x}{:02x}{:02x}".format(
            int(rgb[0]*255),
            int(rgb[1]*255),
            int(rgb[2]*255)
        ))

    return colors


# --------------------------------------------------
# 4. DATASET_RANGE (phylum)
# --------------------------------------------------
def build_range(tree_file, output):

    with open(tree_file) as f:
        newick = f.read()

    leaves = extract_leaves(newick)

    groups = defaultdict(list)
    for leaf in leaves:
        groups[extract_phylum(leaf)].append(leaf)

    phyla = sorted(groups.keys())
    colors = generate_colors(len(phyla))
    cmap = dict(zip(phyla, colors))

    with open(output, "w") as out:

        # TEMPLATE DATASET_RANGE
        out.write("DATASET_RANGE\n")
        out.write("SEPARATOR COMMA\n")
        out.write("DATASET_LABEL,Phylum ranges\n")
        out.write("COLOR,#000000\n\n")

        out.write("RANGE_TYPE,box\n")
        out.write("RANGE_COVER,clade\n\n")

        out.write("DATA\n")

        # CONTAINS== → iTOL regroupe automatiquement
        for phylum in phyla:
            color = cmap[phylum]

            out.write(
                f"CONTAINS=={phylum},,"
                f"{color},,"
                f"{color},solid,1,"
                f"{phylum},#000000,1,normal\n"
            )


# --------------------------------------------------
# 5. DATASET_BINARY (triangles)
# --------------------------------------------------
def build_binary(marker_file, output):

    with open(marker_file) as f:
        markers = [l.strip() for l in f if l.strip()]

    with open(output, "w") as out:

        # TEMPLATE DATASET_BINARY
        out.write("DATASET_BINARY\n")
        out.write("SEPARATOR COMMA\n")
        out.write("DATASET_LABEL,Query\n")
        out.write("COLOR,#ff0000\n\n")

        # triangle droit
        out.write("FIELD_SHAPES,4\n")
        out.write("FIELD_LABELS,query\n")
        out.write("FIELD_COLORS,#ff0000\n\n")

        out.write("DATA\n")

        # 1 = rempli → triangle visible
        for m in markers:
            out.write(f"{m},1\n")


# --------------------------------------------------
# 6. DATASET_SIMPLEBAR (longueurs)
# --------------------------------------------------
def build_bar(length_file, output):

    data = {}

    with open(length_file) as f:
        next(f)  # skip header
        for line in f:
            name, length = line.strip().split(",")
            data[name] = length

    with open(output, "w") as out:

        # TEMPLATE DATASET_SIMPLEBAR
        out.write("DATASET_SIMPLEBAR\n")
        out.write("SEPARATOR COMMA\n")
        out.write("DATASET_LABEL,Protein length\n")
        out.write("COLOR,#3498db\n\n")

        out.write("WIDTH,500\n")
        out.write("SHOW_VALUE,1\n\n")

        out.write("DATA\n")

        for k, v in data.items():
            out.write(f"{k},{v}\n")


# --------------------------------------------------
# 7. MAIN
# --------------------------------------------------
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()

    parser.add_argument("-t", "--tree", required=True)
    parser.add_argument("-m", "--markers", required=True)
    parser.add_argument("-l", "--lengths", required=True)
    parser.add_argument("-o", "--outprefix", required=True)

    args = parser.parse_args()

    build_range(args.tree, args.outprefix + "_range.txt")
    build_binary(args.markers, args.outprefix + "_binary.txt")
    build_bar(args.lengths, args.outprefix + "_bar.txt") 