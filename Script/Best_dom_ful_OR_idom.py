#!/usr/bin/env python3

import argparse
import math

"""
best_domain_info.py

Extrait les informations de domaines à partir d'un fichier HMMER
hmmscan (--domtblout).

Le script :
- Parse les hits de domaines du fichier domtblout.
- Regroupe les hits par protéine.
- Supprime les domaines chevauchants en conservant celui ayant la
  meilleure i-Evalue.
- Génère un fichier TSV contenant tous les domaines non redondants.
- Génère un fichier TSV filtré selon des seuils sur les
  log10(full E-value) et/ou log10(i-Evalue).

Colonnes de sortie :
Protein_ID, domain, log_full_Evalue, log_iEvalue,
q_start, q_end, hmm_start, hmm_end, description

Exemple :
    best_domain_info.py \
        -i input.domtblout \
        -o domains.tsv \
        -b domains_filtered.tsv \
        --full_thr -10 \
        --dom_thr -10
"""

# -----------------------------
# Utils
# -----------------------------

def get_protein_id(query):
    parts = query.split("|")
    if len(parts) < 3:
        return query
    return parts[1] + "|" + parts[2].split("~")[0]

# pour gerer les evalue a zero ou proche de zero vu qu'on ne peut pas prendre le log de 0
def safe_log10(x):
    x = float(x)
    if x <= 0:
        return -1000
    return math.log10(x)

# Gerer les chevauchement des domaines pour une meme proteine 
def overlap(a1, a2, b1, b2):
    return not (a2 < b1 or b2 < a1)


def is_better(d1, d2):
    # lower i-evalue is better
    return d1["i_evalue"] < d2["i_evalue"]


# -----------------------------
# Parse
# -----------------------------

def parse_domtblout(path):

    data = {}

    with open(path) as f:
        for line in f:

            if line.startswith("#") or not line.strip():
                continue

            fields = line.split()

            domain = fields[0]
            query = fields[3]

            full_evalue = float(fields[6])
            i_evalue = float(fields[12])

            hmm_start = int(fields[15])
            hmm_end = int(fields[16])

            q_start = int(fields[17])
            q_end = int(fields[18])

            desc = " ".join(fields[22:])

            prot = get_protein_id(query)

            data.setdefault(prot, []).append({
                "domain": domain,
                "full_evalue": full_evalue,
                "i_evalue": i_evalue,
                "log_full": safe_log10(full_evalue),
                "log_i": safe_log10(i_evalue),
                "q_start": q_start,
                "q_end": q_end,
                "hmm_start": hmm_start,
                "hmm_end": hmm_end,
                "desc": desc
            })
    return data


# -----------------------------
# Collapse overlaps
# -----------------------------

def collapse_overlaps(hits):

    # sort by best first (smallest i-evalue)
    hits = sorted(hits, key=lambda x: x["i_evalue"])

    selected = []

    for h in hits:
        keep = True

        for s in selected:
            if overlap(h["q_start"], h["q_end"], s["q_start"], s["q_end"]):

                # if overlap -> keep only better
                if not is_better(h, s):
                    keep = False
                    break

        if keep:
            selected.append(h)

    # restore order along sequence
    return sorted(selected, key=lambda x: x["q_start"])


# -----------------------------
# Write output
# -----------------------------

def write_outputs(data, out_all, out_filtered, full_thr, dom_thr):

    header = (
        "Protein_ID\tdomain\tlog_full_Evalue\tlog_iEvalue\t"
        "q_start\tq_end\thmm_start\thmm_end\tdescription\n"
    )

    with open(out_all, "w") as fout, open(out_filtered, "w") as fbest:

        fout.write(header)
        fbest.write(header)

        for prot, hits in data.items():

            # STEP 1: remove overlaps
            clean_hits = collapse_overlaps(hits)

            for h in clean_hits:

                line = (
                    f"{prot}\t{h['domain']}\t{h['log_full']}\t{h['log_i']}\t"
                    f"{h['q_start']}\t{h['q_end']}\t"
                    f"{h['hmm_start']}\t{h['hmm_end']}\t"
                    f"{h['desc']}\n"
                )

                fout.write(line)

                # STEP 2: filtering (LOG SCALE)
                keep = True

                full_ok = (full_thr is None) or (h["log_full"] < full_thr)
                dom_ok  = (dom_thr is None) or (h["log_i"] < dom_thr)

                keep = full_ok or dom_ok
                if keep:
                    fbest.write(line)


# -----------------------------
# Main
# -----------------------------

def main():

    parser = argparse.ArgumentParser()

    parser.add_argument("-i", "--input", required=True)
    parser.add_argument("-o", "--output_all", required=True)
    parser.add_argument("-b", "--output_filtered", required=True)

    parser.add_argument("--full_thr", type=float, default=None)
    parser.add_argument("--dom_thr", type=float, default=None)

    args = parser.parse_args()

    data = parse_domtblout(args.input)

    write_outputs(
        data,
        args.output_all,
        args.output_filtered,
        args.full_thr,
        args.dom_thr
    )


if __name__ == "__main__":
    main()