#!/usr/bin/env python3

"""
SCRIPT : Génération d’un fichier iTOL pour colorer un arbre phylogénétique
OBJECTIF :
- Lire un arbre IQ-TREE (format Newick)
- Extraire les feuilles (taxa)
- Identifier le phylum de chaque séquence
- Générer un fichier iTOL utilisant le template TREE_COLORS
  avec le type "range" pour colorer les labels/clades

TEMPLATE UTILISÉ :
→ TREE_COLORS (template officiel iTOL)
→ TYPE = range

Pourquoi "range" ?
- Permet de colorer le fond des labels (mode "Label" dans iTOL)
- Permet aussi de colorer les clades (mode "Clade")
- Recommandé par la documentation iTOL (Colored ranges)
"""

import re
from collections import defaultdict


# --------------------------------------------------
# 1. EXTRACTION DU PHYLUM
# --------------------------------------------------
def extract_phylum(label):
    """
    Extrait le phylum depuis le label IQ-TREE.

    Exemple de label :
    ..._Eukaryota-Arthropoda-Arachnida-...

    → On récupère "Arthropoda"
    """
    try:
        tax_part = label.split("_Eukaryota-")[1]
        return tax_part.split("-")[0]
    except:
        return "Unknown"


# --------------------------------------------------
# 2. EXTRACTION DES FEUILLES (TAXA)
# --------------------------------------------------
def extract_leaves(newick):
    """
    Extrait uniquement les feuilles de l’arbre Newick.

    IMPORTANT :
    - On enlève les valeurs bootstrap (ex: 100/100)
    - On garde uniquement les vrais noms biologiques
    """

    tokens = re.split(r"[(),;]", newick)
    leaves = []

    for t in tokens:
        t = t.strip()

        if not t:
            continue

        # supprimer la longueur de branche (après ":")
        t = t.split(":")[0]

        # filtrer les valeurs bootstrap
        if re.match(r"^[0-9]+(\.[0-9]+)?(/[0-9]+(\.[0-9]+)?)?$", t):
            continue

        # garder uniquement les labels contenant "Eukaryota"
        if "Eukaryota" in t:
            leaves.append(t)

    return leaves


# --------------------------------------------------
# 3. GÉNÉRATION DE COULEURS AUTOMATIQUES
# --------------------------------------------------
def generate_colors(n):
    """
    Génère n couleurs distinctes (format HEX).
    Utilise l’espace HSV pour avoir des couleurs bien séparées.
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
# 4. CONSTRUCTION DU FICHIER iTOL
# --------------------------------------------------
def build_itol_ranges(input_tree, output_file):

    # Lecture du fichier Newick
    with open(input_tree) as f:
        newick = f.read()

    # Extraction des feuilles
    leaves = extract_leaves(newick)

    # Mapping : feuille → phylum
    phylum_map = {}
    phylum_groups = defaultdict(list)

    for leaf in leaves:
        phylum = extract_phylum(leaf)

        phylum_map[leaf] = phylum
        phylum_groups[phylum].append(leaf)

    # Liste des phylum uniques
    phyla = sorted(phylum_groups.keys())

    # Attribution d'une couleur par phylum
    colors = generate_colors(len(phyla))
    color_map = dict(zip(phyla, colors))

    # --------------------------------------------------
    # ÉCRITURE DU FICHIER iTOL
    # --------------------------------------------------
    with open(output_file, "w") as out:

        """
        TEMPLATE UTILISÉ : TREE_COLORS

        SEPARATOR TAB :
        → les colonnes sont séparées par des tabulations

        TYPE UTILISÉ : range

        FORMAT DES LIGNES :
        node_id    range    couleur    label

        → "range" permet de créer des zones colorées
        → interprétées dans iTOL comme :
            - fond des labels (mode Label)
            - fond des clades (mode Clade)
        """

        out.write("TREE_COLORS\n")
        out.write("SEPARATOR TAB\n")
        out.write("DATA\n")

        # Écriture des données
        for leaf in leaves:
            phylum = phylum_map[leaf]
            color = color_map[phylum]

            # Application du type "range"
            out.write(f"{leaf}\trange\t{color}\t{phylum}\n")


# --------------------------------------------------
# 5. UTILISATION EN LIGNE DE COMMANDE
# --------------------------------------------------
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Génère un fichier iTOL (TREE_COLORS) pour colorer les phylum"
    )

    parser.add_argument("-i", "--input", required=True,
                        help="Fichier arbre Newick (IQ-TREE)")
    parser.add_argument("-o", "--output", required=True,
                        help="Fichier de sortie iTOL")

    args = parser.parse_args()

    build_itol_ranges(args.input, args.output)