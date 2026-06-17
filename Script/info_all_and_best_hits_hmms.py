#!/usr/bin/env python3

import argparse
import math

"""
USAGE :

# TSV complet seulement
python script.py \
    -i file.hmms \
    -o all.tsv

# TSV complet + best hits avec seuil simple
python script.py \
    -i file.hmms \
    -o all.tsv \
    --best_output best.tsv \
    --full_evalue -120 \
    --dom_evalue -120

# TSV complet + best hits avec intervalle
python script.py \
    -i file.hmms \
    -o all.tsv \
    --best_output best.tsv \
    --full_evalue -120 -70 \
    --dom_evalue -120 -70

# TSV complet + filtre domaines observés
python script.py \
    -i file.hmms \
    -o all.tsv \
    --best_output best.tsv \
    --full_evalue -120 \
    --dom_evalue -120 \
    --obs_domains 1
"""


def get_keys_uniq(name):
    """
    Extrait une clé unique :
    GCA_xxx|PROTEIN_ID
    """
    parts = name.split("|")

    if len(parts) < 3:
        return None

    genome = parts[1]
    protein = parts[2].split("~")[0]

    return genome + "|" + protein


def check_evalue(value, threshold):
    """
    Vérifie si une evalue respecte le seuil.

    threshold peut être :
    - [max[
    - [min, max[
    """

    if threshold is None:
        return True

    # seuil simple
    if len(threshold) == 1:
        return value < threshold[0]

    # intervalle
    elif len(threshold) == 2:
        low, high = sorted(threshold)
        return low <= value < high

    else:
        raise ValueError(
            "Threshold must contain 1 or 2 values"
        )


def safe_log10(value):
    """
    HMMER peut retourner 0 pour des e-values
    extrêmement petites. Cette fonction permet de gerer ce cas car log10(0) donnera une erreur
    """

    value = float(value)

    if value == 0:
        return -1000 # je prend -1000 pour les evalues de 0

    return math.log10(value)


def extract_target_from_hmmer_file(
    hmmers_file,
    output,
    best_output=None,
    full_thr=None,
    dom_thr=None,
    obs_dom=None
):

    with open(hmmers_file) as f, \
         open(output, "w") as fout, \
         (open(best_output, "w") if best_output else open("/dev/null", "w")) as fbest:

        header = (
            "ID\tfull_log10_evalue\tfull_score\t"
            "dom_log10_evalue\tdom_score\t"
            "exp_domains\tobs_domains\n"
        )

        fout.write(header)

        if best_output:
            fbest.write(header)

        for line in f:

            if line.startswith("#") or line.strip() == "":
                continue

            fields = line.split()

            target = fields[0]

            extracted_id = get_keys_uniq(target)

            if not extracted_id:
                continue

            # extraction valeurs
            ID = extracted_id

            full_evalue = safe_log10(fields[4])
            full_score = fields[5]

            dom_evalue = safe_log10(fields[7])
            dom_score = fields[8]

            exp_domains = fields[10]
            obs_domains = int(fields[15])

            # écrire TSV complet
            fout.write(
                f"{ID}\t{full_evalue}\t{full_score}\t"
                f"{dom_evalue}\t{dom_score}\t"
                f"{exp_domains}\t{obs_domains}\n"
            )

            # -------------------------
            # filtre best_hits
            # garder si full OU dom passent
            # -------------------------

            conditions = []

            if full_thr is not None:
                conditions.append(
                    check_evalue(full_evalue, full_thr)
                )

            if dom_thr is not None:
                conditions.append(
                    check_evalue(dom_evalue, dom_thr)
                )

            # OR logique
            keep = any(conditions) if conditions else True

            # filtre nb domaines observés
            if obs_dom is not None:
                keep = keep and (obs_domains == obs_dom)

            # écrire best hits
            if keep and best_output:

                fbest.write(
                    f"{ID}\t{full_evalue}\t{full_score}\t"
                    f"{dom_evalue}\t{dom_score}\t"
                    f"{exp_domains}\t{obs_domains}\n"
                )


def main():

    parser = argparse.ArgumentParser(
        description="Parse HMMER tblout + optional filtering"
    )

    parser.add_argument(
        "-i",
        "--input",
        required=True,
        help="HMMER output file"
    )

    parser.add_argument(
        "-o",
        "--output",
        required=True,
        help="Full TSV output"
    )

    parser.add_argument(
        "--best_output",
        help="Filtered best hits TSV"
    )

    parser.add_argument(
        "--full_evalue",
        type=float,
        nargs="+",
        help=(
            "Full evalue threshold: "
            "one value or interval "
            "(ex: -120 OR -120 -70)"
        )
    )

    parser.add_argument(
        "--dom_evalue",
        type=float,
        nargs="+",
        help=(
            "Domain evalue threshold: "
            "one value or interval"
        )
    )

    parser.add_argument(
        "--obs_domains",
        type=int,
        help="Filter on observed domains"
    )

    args = parser.parse_args()

    extract_target_from_hmmer_file(
        args.input,
        args.output,
        args.best_output,
        args.full_evalue,
        args.dom_evalue,
        args.obs_domains
    )


if __name__ == "__main__":
    main()