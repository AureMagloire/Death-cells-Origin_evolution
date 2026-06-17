#!/usr/bin/env python3

import sys
"""
Usage :  Name_domain_fasta.py input.fasta input_list_domain.tsv output.fasta

Description :
    Filtre le fichier FASTA à partir du TSV contenant la liste des domaine filtré de chaque genome (GCA_019633485.1|KAG8974145.1  domai1$domain2) et remplace les annotations des en-têtes par les domaines associés.
   NB :  Seules les protéines présentes dans le TSV sont conservées dans le fichier de sortie.
"""
# ----------------------------
# 1. TSV → dictionnaire
# ----------------------------
def load_tsv(tsv_file):
    mapping = {}

    with open(tsv_file, "r") as f:

        # sauter l'en-tête
        next(f)

        for line in f:
            if not line.strip():
                continue

            parts = line.rstrip().split("\t")

            prot_id = parts[0]
            domain = parts[1]

            if prot_id not in mapping:
                mapping[prot_id] = []

            mapping[prot_id].append(domain)

    # concaténation des domaines avec #
    for prot_id in mapping:
        mapping[prot_id] = "#".join(mapping[prot_id])
    #print(mapping)

    return mapping


# ----------------------------
# 2. Fonction fournie (à adapter si besoin)
# ----------------------------
def extract_prot_id(header):
    """
    Exemple header :
    >...|GCA_019633485.1|KAG8974145.1~2600229=...$...
    On extrait : GCA_019633485.1|KAG8974145.1
    """
    header = header.lstrip(">")
    parts = header.split("|")
    prot_id = parts[1] + "|" + parts[2].split("~")[0]
    return prot_id


# ----------------------------
# 3. FASTA parser simple
# ----------------------------
def read_fasta(fasta_file):
    header = None
    seq = []

    with open(fasta_file, "r") as f:
        for line in f:
            line = line.strip()
            if line.startswith(">"):
                if header:
                    yield header, "".join(seq)
                header = line
                seq = []
            else:
                seq.append(line)

        if header:
            yield header, "".join(seq)


# ----------------------------
# 4. Main
# ----------------------------
def main(fasta_file, tsv_file, output_file):
    mapping = load_tsv(tsv_file)

    with open(output_file, "w") as out:
        for header, seq in read_fasta(fasta_file):

            prot_id = extract_prot_id(header)

            domains = mapping.get(prot_id, "no_domain")

            # reconstruire le header proprement
            base_header = header.split("$")[0]
            new_header = f"{base_header}${domains}"

            out.write(new_header + "\n")
            out.write(seq + "\n")
# il faut que je revoie le cas ou prot_id n'est pas dans mapping le cas ou aucun domain n'est trouvé 

# ----------------------------
# 5. Run
# ----------------------------
if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python script.py input.fasta input.tsv output.fasta")
        sys.exit(1)

    main(sys.argv[1], sys.argv[2], sys.argv[3])