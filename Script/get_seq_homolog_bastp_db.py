#!/usr/bin/env python3
import argparse
import os 
'''
Ce script recuperes dans la base de données, la sequence des homologue trouvé par blastp
Algo : parcoure les ligne commencant par ">" dans le fichier de blasp

Donne un fichier homologue.faa

'''


def get_unique_id(name):
    """
    Extrait la clé unique : GCA_xxx|PROTEIN_ID en prenant en entrée le nom dans le fichier BLASTP.
    """
    parts = name.split("|")
    if len(parts) < 3:
        return None
    genome = parts[1]
    protein = parts[2].split("~")[0]
    return genome + "|" + protein


def get_keys_uniq(blastp_file):

    key_uniq = []

    with open(blastp_file, 'r') as file:
        for line in file:
            line = line.strip()
            if line.startswith(">"):
                clé = get_unique_id(line)
                key_uniq.append(clé)
    return key_uniq



# recuperer les sequences dans la base de données et les mettre dans un fichier 

def extract_sequences(database, key_uniq, output):

    write = False

    with open(database) as db, open(output, "w") as out:

        for line in db:

            if line.startswith(">"):

                header = line.split("=")[0]
                key = get_unique_id(header)
                if key in key_uniq:
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

        key_uniq = get_keys_uniq(blast_file)

        # créer un nom de fichier de sortie propre a chaque proteine
        prefix = os.path.splitext(os.path.basename(blast_file))[0] 

        output = f"{prefix}_homologue.faa"
        print(f"Traitement : {blast_file}")
        print(f"{len(key_uniq)} sequences homologue trouvées")
        print(f"sequences homologues de {prefix}  stockée dans : {output}")

        # extraire les séquences correspondantes dans la database
        extract_sequences(args.database, key_uniq, output)


if __name__ == "__main__":
    main()


# UNE AUTRE FACON DE RECUPERER LES SEQUENCE HOMOLOGUE (jean piere ) :
# récuperer toutes les identifiant dans le fichier bastp et les metre dans un fichier.txt et faire un grep -A1 -f fichier.txt db.faa > fichier_homology.faa
# Mais avant ca il faut que les sequences dans la base de données soient sur une ligne avec la commande : awk '{if(NR==1) {print $0} else {if($0 ~ /^>/) {print "\n"$0} else {printf $0}}}' surplusieurslignes.fasta > uneligne.fasta
