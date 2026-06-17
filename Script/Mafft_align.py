#!/usr/bin/env python3

'''
Ce script prend en entré les fichier de sequences homologue de chaque proteines et faire un alignement multiple avec l'outils mafft
USAGE : Mafft.py -i fichier.faa[,...,fichier.faa] 

'''

import argparse
import subprocess
import os


def run_mafft(input_file):

    # récupérer le nom du fichier sans chemin
    basename = os.path.basename(input_file)

    # enlever l'extension .faa ou fasta
    name = os.path.splitext(basename)[0].replace("_homology","")

    # créer le fichier de sortie
    output = f"{name}.MAFFT"

    cmd = ["mafft", "--auto", "--reorder", input_file]

    with open(output, "w") as outfile:
        subprocess.run(cmd, stdout=outfile)

    #print(f"Alignment terminé : {output}")


def main():

    parser = argparse.ArgumentParser(description="Run MAFFT on homology files")

    parser.add_argument( "-i", "--input", nargs="+",required=True, help="Homology fasta files" )
    parser.add_argument( "-t", "--threads", help="GPU" )

    args = parser.parse_args()

    for file in args.input:
        basename = os.path.basename(file)
        print(f"....running alignement for {basename}")
        run_mafft(file)


if __name__ == "__main__":
    main()