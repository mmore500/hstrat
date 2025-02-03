import argparse
from functools import partial
import sys

from colorclade import draw_colorclade_tree
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from hstrat._auxiliary_lib import alifestd_try_add_ancestor_list_col


def _parse_args() -> argparse.Namespace:
    """Helper function to parse command line arguments."""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-o",
        "--open",
        action="store_true",
    )
    parser.add_argument(
        "--true-df-path",
        type=str,
    )
    parser.add_argument(
        "--reconst-df-path",
        type=str,
    )
    parser.add_argument(
        "--img-path",
        type=str,
        default="/tmp/visualized_reconst_phylogenies.png",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = _parse_args()
    sys.setrecursionlimit(100000)
    true_df = pd.read_csv(args.true_df_path)
    reconst_df = pd.read_parquet(args.reconst_df_path)

    true_df["taxon_label"] = true_df["taxon_label"].apply(lambda x: x[:5])
    reconst_df["taxon_label"] = reconst_df["taxon_label"].apply(
        lambda x: x and x[:5]
    )

    true_df = alifestd_try_add_ancestor_list_col(true_df)
    reconst_df = alifestd_try_add_ancestor_list_col(reconst_df)

    fig, axes = plt.subplots(1, 2)
    draw_colorclade_tree(
        true_df,
        taxon_name_key="taxon_label",
        ax=axes.flat[0],
        backend="biopython",
        label_tips=True,
    )
    draw_colorclade_tree(
        reconst_df,
        taxon_name_key="taxon_label",
        ax=axes.flat[1],
        backend="biopython",
        label_tips=False,
    )
    axes.flat[0].set_xscale(
        "function", functions=(lambda x: x**10, lambda x: x**0.1)
    )
    axes.flat[0].set_xlim(0, len(true_df["depth"].unique()) + 5)
    axes.flat[1].set_xlim(reversed(axes.flat[1].get_xlim()))
    fig.set_size_inches(20, 20)
    plt.tight_layout()
    plt.savefig(args.img_path)
    if args.open:
        plt.show()
