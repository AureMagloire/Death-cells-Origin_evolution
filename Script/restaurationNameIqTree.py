#!/usr/bin/env python3
import sys
"""
Ce script renormme les sequences dans l'arbre donné par Iqtree pour le rendre conforme au niom des sequences dans l'alignement afin de faire une meilleur visualisation

Usage : restaurationNameIqTree.py treefile, logfile, alignment
"""
def get_unique_id(name):
    """
    Extrait la clé unique : GCA_xxx|PROTEIN_ID en prenant en entré le nom que IQtree designe comme original
    """
    parts = name.split("|")

    if len(parts) < 3:
        return None

    genome = parts[1]
    protein = parts[2].split("~")[0]

    return genome + "|" + protein


def traduit(treefile, logfile, alignment):

    # -------- lire le log IQ-TREE --------
    dico = {}

    with open(logfile) as log:

        try:
            LOG = log.read().split("WARNING: Some sequence names are changed as follows:")[1].split("\n\n")[0].strip().split("\n")

        except IndexError:
            print("Aucune modification trouvée dans le log")
            LOG = []

        for line in LOG:

            orig = line.split("->")[0].strip()
            mod  = line.split("->")[1].strip()

            unique_id = get_unique_id(orig)

            if unique_id:
                dico[unique_id] = mod


    # -------- lire l'alignement --------
    align_names = {}

    with open(alignment) as aln:

        for line in aln:

            if line.startswith(">"):

                header = line[1:].strip()

                uid = get_unique_id(header)

                if uid:
                    align_names[uid] = header


    # -------- lire l'arbre --------
    with open(treefile) as f:
        tree = f.read()


    # -------- remplacer les noms --------
    for uid in dico:

        if uid in align_names:

            mod_name = dico[uid]
            vrai_nom = align_names[uid]

            tree = tree.replace(mod_name, vrai_nom)


    # -------- écrire le fichier corrigé --------
    outfile = treefile + ".restor"

    with open(outfile, "w") as f:
        f.write(tree)

    #print("Arbre corrigé :", outfile)


if __name__ == "__main__":

    treefile  = sys.argv[1]
    logfile   = sys.argv[2]
    alignment = sys.argv[3]

    traduit(treefile, logfile, alignment)