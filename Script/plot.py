#!/usr/bin/env python3

import argparse
import pandas as pd
import matplotlib.pyplot as plt


def main():
    parser = argparse.ArgumentParser(description="Plot HMMER TSV")

    parser.add_argument("-i", "--input", required=True)
    parser.add_argument("-o", "--output", default="plot.png")

    parser.add_argument("--y", required=True,
                        help="Column to plot (full_score, dom_score, obs_domains, etc.)")

    parser.add_argument("--top", type=int, default=None,
                        help="Show only top N targets")

    args = parser.parse_args()

    # LOAD
    df = pd.read_csv(args.input, sep="\t")

    # numeric conversion (important for plotting)
    df[args.y] = pd.to_numeric(df[args.y], errors="coerce")

    # sort by score (useful biologically)
    df = df.sort_values(args.y, ascending=False)

    # top N if needed
    if args.top:
        df = df.head(args.top)

    # PLOT
    plt.figure(figsize=(12, 6))

    plt.bar(df["ID"], df[args.y])

    plt.xlabel("ID")
    plt.ylabel(args.y)
    plt.title(f"{args.y} per ID")

    plt.xticks(rotation=90)
    plt.tight_layout()

    plt.savefig(args.output, dpi=300)

    print(f"Saved: {args.output}")
    print(f"{len(df)} targets plotted")


if __name__ == "__main__":
    main()