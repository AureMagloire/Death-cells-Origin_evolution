#!/usr/bin/env python3

import argparse
import subprocess
import os
'''
Ce script constuit les arbres phylogenetique de chaque proteine avec IQtree

Ex Usage : Iqtree.py -f MLKL_hs.MAFFT  RIPK1_hs.MAFFT RIPK3_hs.MAFFT  TLR3_hs.MAFFT  TLR4_hs.MAFFT  TRADD_hs.MAFFT  TRIF_hs.MAFFT  ZBP1_hs.MAFFT -t 20

'''

def run_iqtree(input_file,threads):

    input_file = os.path.abspath(input_file) # le chemin absolue des fichier mafft

    basename = os.path.basename(input_file)
    prefix = os.path.splitext(basename)[0]

    # créer le dossier au nom de chaque proteine (prefix) pour stocker le resultat de chaque proteine
    os.makedirs(prefix, exist_ok=True)

    print(f"...Running IQ-TREE for {basename}")

    cmd = [ "iqtree3", "-s", input_file, "-T",str(threads), "-m", "LG+G", "-B", "1000", "-alrt", "100", "--prefix", prefix]
    
    subprocess.run(cmd, cwd=prefix, check=True)


def main():

    parser = argparse.ArgumentParser(description="Run IQ-TREE on MAFFT alignments")

    parser.add_argument("-f", "--input", nargs="+", required=True, help="MAFFT alignment files" )
    parser.add_argument("-t", "--threads",default="AUTO",help="Number of threads for IQ-TREE (default: AUTO)")

    args = parser.parse_args()

    for file in args.input:
         run_iqtree(file, args.threads)


if __name__ == "__main__":
    main()