#!/usr/bin/env python3

import re
from collections import defaultdict

# ----------------------------
# Extract phylum
# ----------------------------
def extract_phylum(label):
    try:
        tax_part = label.split("_Eukaryota-")[1]
        return tax_part.split("-")[0]
    except:
        return "Unknown"


# ----------------------------
# CLEAN IQTREE NEWICK TOKENS
# ----------------------------
def extract_leaves(newick):
    """
    Extract only real taxa labels (remove bootstrap / node values).
    """

    # remove line breaks
    newick = newick.replace("\n", "")

    # split by commas and parentheses logic
    tokens = re.split(r"[(),;]", newick)

    leaves = []

    for t in tokens:
        t = t.strip()

        if not t:
            continue

        # remove branch lengths
        t = t.split(":")[0]

        # FILTER OUT bootstrap-like values
        if re.match(r"^[0-9]+(\.[0-9]+)?(/[0-9]+(\.[0-9]+)?)?$", t):
            continue

        # must contain biological label
        if "Eukaryota" in t:
            leaves.append(t)

    return leaves


# ----------------------------
# colors
# ----------------------------
def generate_colors(n):
    import colorsys
    colors = []
    for i in range(n):
        h = i / n
        rgb = colorsys.hsv_to_rgb(h, 0.6, 0.9)
        colors.append("#{0:02x}{1:02x}{2:02x}".format(
            int(rgb[0]*255), int(rgb[1]*255), int(rgb[2]*255)
        ))
    return colors


# ----------------------------
# MAIN
# ----------------------------
def build_itol(input_tree, output_file):

    with open(input_tree) as f:
        newick = f.read()

    leaves = extract_leaves(newick)

    phylum_map = {}
    phylum_groups = defaultdict(list)

    for leaf in leaves:
        phylum = extract_phylum(leaf)
        phylum_map[leaf] = phylum
        phylum_groups[phylum].append(leaf)

    phyla = sorted(phylum_groups.keys())
    colors = generate_colors(len(phyla))
    color_map = dict(zip(phyla, colors))

    with open(output_file, "w") as out:

        out.write("DATASET_COLORSTRIP\n")
        out.write("SEPARATOR TAB\n")
        out.write("DATASET_LABEL\tPhylum annotation\n")
        out.write("COLOR\t#000000\n")
        out.write("STRIP_WIDTH\t25\n")
        out.write("MARGIN\t5\n\n")

        out.write("LEGEND_TITLE\tPhylum\n")
        out.write("LEGEND_SHAPES\t" + "\t".join(["1"]*len(phyla)) + "\n")
        out.write("LEGEND_COLORS\t" + "\t".join([color_map[p] for p in phyla]) + "\n")
        out.write("LEGEND_LABELS\t" + "\t".join(phyla) + "\n\n")

        out.write("DATA\n")

        for leaf in leaves:
            phylum = phylum_map.get(leaf, "Unknown")
            color = color_map.get(phylum, "#000000")
            out.write(f"{leaf}\t{color}\t{phylum}\n")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", required=True)
    parser.add_argument("-o", "--output", required=True)

    args = parser.parse_args()

    build_itol(args.input, args.output)