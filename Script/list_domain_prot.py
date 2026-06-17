#!/usr/bin/env python3

import argparse
"""
Ce script donne un fichier resultat contenant les proteine homologue et la liste de leur domain
USAGE : python list_domain.py.py \
    -i all_domains.faa \ # l' ensemble des proteine (seed et d'autre homologue et paralogue comme les champions)
    -t domains.tsv \ " tsv contenat des info des domaine pour chaque proteine
    -o result.tsv
"""

def get_keys_uniq(name):
    parts = name.split("|")
    if len(parts) < 3:
        return None

    genome = parts[1]
    protein = parts[2].split("~")[0]

    return f"{genome}|{protein}"


def extract_id_prot(all_prot_file):
    prot_ids = []

    with open(all_prot_file) as f:
        for line in f:
            if line.startswith(">"):
                header = line.split("=")[0]
                key = get_keys_uniq(header)

                if key is not None and key not in prot_ids:
                    prot_ids.append(key)

    return prot_ids


def load_domains(tsv_file):
    domain_dict = {}

    with open(tsv_file) as f:
        next(f)  # saute l'en-tête

        for line in f:
            fields = line.rstrip().split("\t")

            prot_id = fields[0]
            domain = fields[1]

            if prot_id not in domain_dict:
                domain_dict[prot_id] = []

            domain_dict[prot_id].append(domain)
            #print(domain_dict)

    return domain_dict


def write_domains(all_prot_file, tsv_file, output_file):

    prot_ids = extract_id_prot(all_prot_file)
    domain_dict = load_domains(tsv_file)

    with open(output_file, "w") as out:

        for prot_id in prot_ids:

            if prot_id in domain_dict:
                domains = "&".join(domain_dict[prot_id])
            else:
                domains = "no_domain"

            out.write(f"{prot_id}\t{domains}\n")


def main():

    parser = argparse.ArgumentParser()

    parser.add_argument("-i", "--input", required=True,
                        help="all protein file")

    parser.add_argument("-t", "--tsv", required=True,
                        help="domain TSV file")

    parser.add_argument("-o", "--output", required=True,
                        help="output file")

    args = parser.parse_args()

    write_domains(args.input, args.tsv, args.output)


if __name__ == "__main__":
    main()