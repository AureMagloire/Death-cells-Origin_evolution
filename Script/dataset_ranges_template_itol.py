#!/usr/bin/env python3

"""
SCRIPT : Génération d’un DATASET_RANGE pour iTOL

OBJECTIF :
- Regrouper les séquences par phylum
- Créer un "range" par phylum
- Visualiser chaque phylum comme une boîte colorée (clade)

TEMPLATE UTILISÉ :
→ DATASET_RANGE (Colored/labeled ranges)

AVANTAGE :
- Permet de colorer directement des clades complets
- Plus propre que TREE_COLORS pour les figures
"""

import re
from collections import defaultdict


# --------------------------------------------------
# 1. EXTRACTION DU PHYLUM
# --------------------------------------------------
def extract_phylum(label):
    """
    Extrait le phylum depuis le label IQ-TREE.

    Exemple :
    ..._Eukaryota-Arthropoda-Arachnida-...

    → retourne "Arthropoda"
    """
    try:
        tax_part = label.split("_Eukaryota-")[1]
        return tax_part.split("-")[0]
    except:
        return "Unknown"


# --------------------------------------------------
# 2. EXTRACTION DES FEUILLES
# --------------------------------------------------
def extract_leaves(newick):
    """
    Récupère uniquement les feuilles (taxa),
    en supprimant les valeurs bootstrap.
    """

    tokens = re.split(r"[(),;]", newick)
    leaves = []

    for t in tokens:
        t = t.strip()
        if not t:
            continue

        t = t.split(":")[0]

        # supprimer bootstrap
        if re.match(r"^[0-9]+(\.[0-9]+)?(/[0-9]+(\.[0-9]+)?)?$", t):
            continue

        if "Eukaryota" in t:
            leaves.append(t)

    return leaves


# --------------------------------------------------
# 3. GÉNÉRATION DE COULEURS
# --------------------------------------------------
def generate_colors(n):
    """
    Génère n couleurs distinctes (HEX)
    """
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
# 4. CONSTRUCTION DU DATASET_RANGE
# --------------------------------------------------
def build_dataset_range(input_tree, output_file):

    with open(input_tree) as f:
        newick = f.read()

    leaves = extract_leaves(newick)

    # regrouper par phylum
    phylum_groups = defaultdict(list)

    for leaf in leaves:
        phylum = extract_phylum(leaf)
        phylum_groups[phylum].append(leaf)

    phyla = sorted(phylum_groups.keys())

    # couleurs par phylum
    colors = generate_colors(len(phyla))
    color_map = dict(zip(phyla, colors))

    # --------------------------------------------------
    # ÉCRITURE DU FICHIER iTOL
    # --------------------------------------------------
    with open(output_file, "w") as out:

        """
        TEMPLATE : DATASET_RANGE

        FORMAT :
        START_NODE_ID,END_NODE_ID,FILL_COLOR,...,LABEL_TEXT

        ASTUCE IMPORTANTE :
        → on utilise CONTAINS== pour regrouper automatiquement
        """

        out.write("DATASET_RANGE\n")
        out.write("SEPARATOR COMMA\n")
        out.write("DATASET_LABEL,Phylum ranges\n")
        out.write("COLOR,#000000\n\n")

        # affichage en boîtes
        out.write("RANGE_TYPE,box\n")
        out.write("RANGE_COVER,clade\n\n")

        out.write("DATA\n")

        for phylum in phyla:
            color = color_map[phylum]

            """
            CONTAINS==phylum :
            → iTOL sélectionne toutes les feuilles contenant ce mot
            → crée automatiquement un range pour ce groupe
            """

            out.write(
                f"CONTAINS=={phylum},,"
                f"{color},,"
                f"{color},solid,1,"
                f"{phylum},#000000,1,normal\n"
            )


# --------------------------------------------------
# 5. MAIN
# --------------------------------------------------
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Génère un DATASET_RANGE iTOL pour colorer les phylum"
    )

    parser.add_argument("-i", "--input", required=True,
                        help="Fichier arbre treefile")
    parser.add_argument("-o", "--output", required=True,
                        help="Fichier iTOL")

    args = parser.parse_args()

    build_dataset_range(args.input, args.output)