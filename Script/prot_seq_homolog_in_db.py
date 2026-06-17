#!/usr/bin/env python3
import argparse
import os 
"""
Ce script recuperes dans la base de données, la sequence des homologue trouvé par blastp
Algo :  a la difference du script get_homologye_db.py, ce script extraire le bloc apres la ligne "Sequences producing significant alignments:" et  parcoure les ligne de ce bloc 

Donne un fichier homology.faa
'''
"""



def get_unique_id(name):
    """
    Extrait la clé unique : GCA_xxx|PROTEIN_ID en prenant en entrée le nom (ex : une ligne ou un header) dans le fichier BLASTP.
    """
    parts = name.split("|")
    if len(parts) < 3:
        return None
    genome = parts[1]
    protein = parts[2].split("~")[0]
    return genome + "|" + protein

def extraire_keys(blastp_file):
    block = ""
    with open(blastp_file) as f:
        lines = f.readlines()

    # Chercher le titre "Sequences producing significant alignments:" 
    start = False
    for line in lines:
        if "Sequences producing significant alignments:" in line:
            start = True
            continue  # passer à la ligne juste après le titre
        if start:
            block += line
            # s'arrêter dès qu'on rencontre une double ligne vide
            if block.endswith("\n\n"):
                block = block.strip()  # enlever les lignes vides en début/fin
                break

# À ce stade, 'block' contient juste le bloc des séquences
    #print(block)

    # Parcourir le bloc de séquences
    keys = []
    for line in block.split("\n"):  # maintenant on itère ligne par ligne
        line = line.strip()
        if line == "":  # ignorer les lignes vides
            continue
        key = get_unique_id(line)
        if key:
            keys.append(key)
    #print(keys)
    return keys



# recuperer les sequences dans la base de données et les mettre dans un fichier 

def extract_sequences(database, keys, output):

    write = False

    with open(database) as db, open(output, "w") as out:

        for line in db:

            if line.startswith(">"):

                header = line.split("=")[0]
                #print(header)
                key = get_unique_id(header) # pour extraire aussi de la bas de donné la cle unique 
                #print(key)
                if key in keys:
                    write = True
                    out.write(line)
                else:
                    write = False

            else:
                if write:
                    out.write(line)


def main():
    parser = argparse.ArgumentParser( description="Récupérer les séquences homologues trouvées par blastp")

    parser.add_argument("-f", "--blastp_file", nargs="+", required=True, help="fichiers blastp")

    parser.add_argument("-db", "--database",required=True, help="fichier database.faa")

    args = parser.parse_args()

    for blast_file in args.blastp_file:

        keys= extraire_keys(blast_file)

        # créer un nom de fichier de sortie propre a chaque proteine
        prefix = os.path.splitext(os.path.basename(blast_file))[0] 

        output = f"{prefix}_homology.faa"

        print(f"Traitement : {blast_file}")
        print(f" {len(keys)} sequences homologues trouvées")
        print(f"sequences homologues de {prefix} stockées dans : {output}")

        # extraire les séquences correspondantes dans la database
        extract_sequences(args.database, keys, output)


if __name__ == "__main__":
    main()


# UNE AUTRE FACON DE RECUPERER LES SEQUENCE HOMOLOGUE (jean piere ) :
# récuperer toutes les identifiant dans le fichier bastp et les metre dans un fichier.txt et faire un grep -A1 -f fichier.txt db.faa > fichier_homology.faa
# Mais avant ca il faut que les sequences dans la base de données soient sur une ligne avec la commande : awk '{if(NR==1) {print $0} else {if($0 ~ /^>/) {print "\n"$0} else {printf $0}}}' surplusieurslignes.fasta > uneligne.fasta
