#!/usr/bin/env python3
'''
Script qui recupere dans le fichier de sortie de hmmsearch, les des info sur les  genomes ayant servir a la creation du profil hmm 
'''

import argparse

# extraction ID unique depuis un header 
def get_keys_uniq(name):
    parts = name.split("|")
    if len(parts) < 3:
        return None
    genome = parts[1]
    protein = parts[2].split("~")[0]
    return genome + "|" + protein


#  extraction IDs depuis alignement MAFFT coupé
def get_ids_from_header(algn_cut_file):
    key_uniq = []

    with open(algn_cut_file, 'r') as file:
        for line in file:
            line = line.strip()
            if line.startswith(">"):
                key = get_keys_uniq(line)
                if key:
                    key_uniq.append(key)

    return set(key_uniq)


#  parsing du fichier de sortie de hmmsearch
def extract_target_from_hmmer_file(hmmers_file, key_uniq, output):

    with open(hmmers_file) as f, open(output, "w") as fout:

        # header UNE SEULE FOIS
        fout.write(
            "ID\ttarget_name\tfull_evalue\tfull_score\t"
            "dom_evalue\tdom_score\texp_domains\tobs_domains\n"
        )

        for line in f:
            if line.startswith("#") or line.strip() == "":
                continue

            fields = line.split()

            target = fields[0]

            extracted_id = get_keys_uniq(target)

            if extracted_id and extracted_id in key_uniq:
                ID = extracted_id
                full_evalue = fields[4]
                full_score = fields[5]
                dom_evalue = fields[7]
                dom_score = fields[8]
                exp_domains = fields[10]
                obs_domains = fields[15]

                fout.write(
                    f"{ID}\t{target}\t{full_evalue}\t{full_score}\t"
                    f"{dom_evalue}\t{dom_score}\t{exp_domains}\t{obs_domains}\n"
                )


def main():
    parser = argparse.ArgumentParser(
        description="Filter HMMER tblout using MAFFT alignment IDs"
    )

    parser.add_argument("-i", "--input", required=True, help="hmmsearch file")
    parser.add_argument("-c", "--cutfile", required=True, help="MAFFT alignment file cut")
    parser.add_argument("-o", "--output", required=True, help="output TSV")

    args = parser.parse_args()

    #  IDs MAFFT coupé
    ids = get_ids_from_header(args.cutfile)

    # filtering HMMER
    extract_target_from_hmmer_file(args.input, ids, args.output)


if __name__ == "__main__":
    main()