#!/usr/bin/env python3

import argparse
from itertools import product
import os
import subprocess
import sys
import typing

from PIL.Image import new
import alifedata_phyloinformatics_convert as apc
from colorclade import draw_colorclade_tree
import matplotlib.pyplot as plt
import pandas as pd
from teeplot import teeplot as tp

from hstrat._auxiliary_lib import (
    alifestd_calc_triplet_distance_asexual,
    alifestd_collapse_unifurcations,
    alifestd_count_leaf_nodes,
    alifestd_mark_node_depth_asexual,
    alifestd_prune_extinct_lineages_asexual,
    alifestd_try_add_ancestor_list_col,
)
from hstrat._auxiliary_lib._alifestd_collapse_unifurcations import _collapse_unifurcations


def to_ascii(
    phylogeny_df: pd.DataFrame, taxon_labels: typing.List[str]
) -> str:
    """Print a sample of the phylogeny dataframe."""
    phylogeny_df = phylogeny_df.copy()
    phylogeny_df["extant"] = phylogeny_df["taxon_label"].isin(taxon_labels)
    phylogeny_df = alifestd_prune_extinct_lineages_asexual(
        phylogeny_df, mutate=True
    ).drop(columns=["extant"])
    phylogeny_df = alifestd_collapse_unifurcations(phylogeny_df, mutate=True)

    dp_tree = apc.RosettaTree(phylogeny_df).as_dendropy
    for nd in dp_tree.preorder_node_iter():
        nd._child_nodes.sort(
            key=lambda nd: max(leaf.taxon.label for leaf in nd.leaf_iter()),
        )
    return dp_tree.as_ascii_plot()


def load_df(path: str) -> pd.DataFrame:
    """Helper function to get the appropriate pandas dataframe save handler."""
    df_load_handlers = {
        ".csv": pd.read_csv,
        ".json": pd.read_json,
        ".pqt": pd.read_parquet,
        ".parquet": pd.read_parquet,
    }
    ext = os.path.splitext(path)[-1]
    try:
        return df_load_handlers[ext](path)
    except KeyError:
        raise ValueError(f"Unsupported dataframe path extension: {ext}")


def sample_reference_and_reconstruction(
    differentia_bitwidth: int,
    surface_size: int,
    fossil_interval: typing.Optional[int],
) -> typing.Dict[
    typing.Union[
        typing.Literal["true"],
        typing.Literal["reconst"],
        typing.Literal["true_dropped_fossils"],
        typing.Literal["reconst_dropped_fossils"],
    ],
    pd.DataFrame,
]:
    """Sample a reference phylogeny and corresponding reconstruction."""
    paths = subprocess.run(
        [
            f"{os.path.dirname(__file__)}/"
            "end2end_tree_reconstruction_with_dstream_surf.sh",
            "--differentia-bitwidth",
            f"{differentia_bitwidth}",
            "--surface-size",
            f"{surface_size}",
            *(
                ["--fossil-interval", f"{fossil_interval}"]
                * (fossil_interval is not None)
            ),
        ],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()

    vars = dict()
    exec(paths, vars)  # hack to load paths from shell script output
    true_phylo_df = load_df(vars["true_phylo_df_path"])
    reconst_phylo_df = alifestd_try_add_ancestor_list_col(
        load_df(vars["reconst_phylo_df_path"]),
    )  # ancestor_list column must be added to comply with alife standard

    assert alifestd_count_leaf_nodes(
        true_phylo_df
    ) == alifestd_count_leaf_nodes(reconst_phylo_df)

    reconst_phylo_df_extant = reconst_phylo_df.copy()
    reconst_phylo_df_extant["extant"] = reconst_phylo_df["is_fossil"] == False
    reconst_phylo_df_no_fossils = alifestd_prune_extinct_lineages_asexual(
        reconst_phylo_df_extant
    )

    true_phylo_df_no_fossils = alifestd_prune_extinct_lineages_asexual(
        true_phylo_df.set_index("taxon_label")
        .drop(
            reconst_phylo_df["taxon_label"][reconst_phylo_df["is_fossil"] == True]  # type: ignore
        )
        .reset_index()
    )

    return {
        "true": true_phylo_df,
        "reconst": reconst_phylo_df,
        "true_dropped_fossils": true_phylo_df_no_fossils,
        "reconst_dropped_fossils": reconst_phylo_df_no_fossils,
    }


def plot_colorclade_comparison(
    true_df: pd.DataFrame, reconst_df: pd.DataFrame
) -> None:
    plt.style.use('dark_background')
    fig, axes = plt.subplots(2, 2)

    new_depths = alifestd_mark_node_depth_asexual(alifestd_collapse_unifurcations(true_df))
    new_depths["depth"] = new_depths["node_depth"]
    draw_colorclade_tree(
        true_df,
        taxon_name_key="taxon_label",
        ax=axes.flat[0],
        backend="biopython",
        label_tips=True,
    )
    draw_colorclade_tree(
        new_depths,
        taxon_name_key="taxon_label",
        ax=axes.flat[2],
        backend="biopython",
        label_tips=False,
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
    axes.flat[0].set_title("True Phylogeny")
    axes.flat[1].set_title("Reconstructed Phylogeny")
    axes.flat[2].set_title("True Phylogeny Unifurcations Dropped")
    plt.tight_layout()


def visualize_reconstruction(
    true_phylo_df: pd.DataFrame,
    reconst_phylo_df: pd.DataFrame,
    *,
    visualize: bool,
    **kwargs,
) -> None:
    """Print a sample of the reference and reconstructed phylogenies."""
    show_taxa = (
        reconst_phylo_df["taxon_label"].dropna().sample(6, random_state=1)
    )
    print("ground-truth phylogeny sample:")
    print(to_ascii(true_phylo_df, show_taxa))
    print()
    print("reconstructed phylogeny sample:")
    print(to_ascii(reconst_phylo_df, show_taxa))

    if visualize:
        true_phylo_df["taxon_label"] = true_phylo_df["taxon_label"].apply(
            lambda x: x[:5]
        )
        reconst_phylo_df["taxon_label"] = reconst_phylo_df[
            "taxon_label"
        ].apply(lambda x: x and x[:5])
        tp.tee(
            plot_colorclade_comparison,
            alifestd_try_add_ancestor_list_col(true_phylo_df),
            alifestd_try_add_ancestor_list_col(reconst_phylo_df),
            teeplot_outattrs=kwargs,
            teeplot_outdir="/tmp",
        )


def test_reconstruct_one(
    differentia_bitwidth: int,
    surface_size: int,
    fossil_interval: typing.Optional[int],
    *,
    visualize: bool,
) -> dict[str, typing.Union[int, float, None]]:
    """Test the reconstruction of a single phylogeny."""
    print("=" * 80)
    print(f"surface_size: {surface_size}")
    print(f"differentia_bitwidth: {differentia_bitwidth}")
    print(f"fossil_interval: {fossil_interval}")

    frames = sample_reference_and_reconstruction(
        differentia_bitwidth,
        surface_size,
        fossil_interval,
    )

    visualize_reconstruction(
        frames["true_dropped_fossils"],
        frames["reconst_dropped_fossils"],
        differentia_bitwidth=differentia_bitwidth,
        surface_size=surface_size,
        fossil_interval=fossil_interval,
        visualize=visualize,
    )
    reconstruction_error = alifestd_calc_triplet_distance_asexual(
        alifestd_collapse_unifurcations(frames["true"]), frames["reconst"]
    )

    reconstruction_error_dropped_fossils = (
        alifestd_calc_triplet_distance_asexual(
            alifestd_collapse_unifurcations(frames["true_dropped_fossils"]),
            frames["reconst_dropped_fossils"],
        )
    )

    print(f"{reconstruction_error=}")
    print(f"{reconstruction_error_dropped_fossils=}")
    assert reconstruction_error < alifestd_count_leaf_nodes(frames["true"])

    return {
        "differentia_bitwidth": differentia_bitwidth,
        "surface_size": surface_size,
        "fossil_interval": fossil_interval,
        "error": reconstruction_error,
        "error_dropped_fossils": reconstruction_error_dropped_fossils,
    }


def _parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--visualize", action="store_true")
    return parser.parse_args()


if __name__ == "__main__":
    sys.setrecursionlimit(100000)
    args = _parse_args()
    reconstruction_errors = pd.DataFrame(
        [
            test_reconstruct_one(
                differentia_bitwidth,
                surface_size,
                fossil_interval,
                visualize=args.visualize,
            )
            for (
                fossil_interval,
                surface_size,
                differentia_bitwidth,
            ) in product((None, 50, 200), (256, 64, 16), (64, 8, 1))
        ]
    )

    reconstruction_errors.to_csv("/tmp/end2end-reconstruction-error.csv")

    # error should increase with decreasing surface size
    assert (
        reconstruction_errors.sort_values(
            ["surface_size", "differentia_bitwidth"], ascending=False
        )
        .groupby("fossil_interval", dropna=False)["error"]
        .is_monotonic_increasing.all()
    )
