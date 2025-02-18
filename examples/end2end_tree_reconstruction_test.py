#!/usr/bin/env python3

import argparse
from itertools import product
import os
import subprocess
import sys
import typing

from Bio.Phylo.BaseTree import Clade as BioClade
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
) -> typing.Dict[str, pd.DataFrame]:
    """Sample a reference phylogeny and corresponding reconstruction."""
    try:
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
    except subprocess.CalledProcessError as e:
        print(f"\033[33m{e.stdout}\033[0m")  # color yellow
        print(f"\033[31m{e.stderr}\033[0m")  # color red
        raise e

    path_vars = dict()  # outparam for exec
    exec(paths, path_vars)  # hack to load paths from shell script output
    true_phylo_df = load_df(path_vars["true_phylo_df_path"])
    reconst_phylo_df = alifestd_try_add_ancestor_list_col(
        load_df(path_vars["reconst_phylo_df_path"]),
    )  # ancestor_list column must be added to comply with alife standard

    assert alifestd_count_leaf_nodes(
        true_phylo_df
    ) == alifestd_count_leaf_nodes(reconst_phylo_df)

    # we use == False and == True here because there are NaN values as well
    reconst_phylo_df_extant = reconst_phylo_df.copy()
    reconst_phylo_df_extant["extant"] = (
        reconst_phylo_df["is_fossil"] == False
    )  # noqa: E712
    reconst_phylo_df_no_fossils = alifestd_prune_extinct_lineages_asexual(
        reconst_phylo_df_extant,
    )

    new_df = (
        true_phylo_df.set_index("taxon_label")
        .drop(
            reconst_phylo_df["taxon_label"][
                reconst_phylo_df["is_fossil"] == True  # type: ignore
            ]  # noqa: E712
        )
        .reset_index()
    )

    true_phylo_df_no_fossils = alifestd_prune_extinct_lineages_asexual(new_df)

    return {
        "exact": true_phylo_df,
        "reconst": reconst_phylo_df,
        "exact_dropped_fossils": true_phylo_df_no_fossils,
        "reconst_dropped_fossils": reconst_phylo_df_no_fossils,
    }


def _label_func(node: BioClade):
    return " " + node.name if node.name and hash(node.name) % 12 == 0 else ""


def plot_colorclade_comparison(
    frames: typing.Dict[str, pd.DataFrame], *, show_fossils: bool
) -> None:
    plotter_kwargs = {
        "taxon_name_key": "taxon_label",
        "backend": "biopython",
        "color_labels": "white",
        "line_width": 2.5,
    }

    plt.style.use("dark_background")
    fig, axes = plt.subplots(3 if show_fossils else 2, 2)

    frames["exact"] = alifestd_collapse_unifurcations(frames["exact"])
    true_df_no_lengths = alifestd_mark_node_depth_asexual(frames["exact"])

    reconst_df_no_lengths = frames["reconst"].copy()
    frames["exact"]["origin_time"] = frames["exact"]["depth"]
    frames["reconst"]["origin_time"] = frames["reconst"]["hstrat_rank"]
    true_df_no_lengths["origin_time"] = true_df_no_lengths["node_depth"]

    if show_fossils:
        frames["exact_dropped_fossils"] = alifestd_collapse_unifurcations(
            frames["exact_dropped_fossils"],
        )
        frames["exact_dropped_fossils"]["origin_time"] = frames[
            "exact_dropped_fossils"
        ]["depth"]
        frames["reconst_dropped_fossils"]["origin_time"] = frames[
            "reconst_dropped_fossils"
        ]["hstrat_rank"]

        draw_colorclade_tree(
            frames["exact_dropped_fossils"],
            ax=axes.flat[0],
            **plotter_kwargs,
            label_tips=_label_func,
        )
        draw_colorclade_tree(
            frames["reconst_dropped_fossils"],
            ax=axes.flat[1],
            **plotter_kwargs,
            label_tips=False,
        )

    draw_colorclade_tree(
        frames["exact"],
        ax=axes.flat[-4],
        **plotter_kwargs,
        label_tips=_label_func,
    )
    draw_colorclade_tree(
        frames["reconst"],
        ax=axes.flat[-3],
        **plotter_kwargs,
        label_tips=False,
    )
    draw_colorclade_tree(
        true_df_no_lengths,
        ax=axes.flat[-2],
        **plotter_kwargs,
        label_tips=_label_func,
    )
    draw_colorclade_tree(
        reconst_df_no_lengths,
        ax=axes.flat[-1],
        **plotter_kwargs,
        label_tips=False,
    )

    # apply a polynomial scale to first two plots, which effectively cause
    # more of the graph to focus on recent data
    axes.flat[0].set_xscale(
        "function", functions=(lambda x: x**10, lambda x: x**0.1)
    )
    axes.flat[0].set_xlim(0, max(frames["exact"]["origin_time"].unique()) + 5)
    axes.flat[1].set_xscale(
        "function", functions=(lambda x: x**10, lambda x: x**0.1)
    )
    axes.flat[1].set_xlim(
        0, max(frames["reconst"]["origin_time"].unique()) + 5
    )

    # flip orientation of right-hand panels
    for i in range(1, len(axes.flat), 2):
        axes.flat[i].set_xlim(reversed(axes.flat[i].get_xlim()))

    fig.set_size_inches(10 * axes.shape[1], 10 * axes.shape[0])
    if show_fossils:
        axes.flat[0].set_title("True Phylogeny Dropped Fossils Recency Scaled")
        axes.flat[1].set_title("Reconstructed Phylogeny Dropped Fossils Recency Scaled")

    middle_descriptor = 'Time Scaled' if show_fossils else 'Recency Scaled'
    axes.flat[-4].set_title(f"True Phylogeny {middle_descriptor}")
    axes.flat[-3].set_title(f"Reconstructed Phylogeny {middle_descriptor}")
    axes.flat[-2].set_title("True Phylogeny Topology Only")
    axes.flat[-1].set_title("Reconstructed Phylogeny Topology Only")
    plt.tight_layout()


def display_reconstruction(
    frames: typing.Dict[str, pd.DataFrame],
    *,
    create_plots: bool,
    **kwargs,
) -> None:
    """Print a sample of the reference and reconstructed phylogenies."""
    show_taxa = (
        frames["reconst_dropped_fossils"]["taxon_label"]
        .dropna()
        .sample(6, random_state=1)
    )
    print("ground-truth phylogeny sample:")
    print(to_ascii(frames["exact_dropped_fossils"], show_taxa))
    print()
    print("reconstructed phylogeny sample:")
    print(to_ascii(frames["reconst_dropped_fossils"], show_taxa))

    if create_plots:
        for df in frames.values():
            df["taxon_label"] = df["taxon_label"].apply(lambda x: x and x[:6])
        tp.tee(
            plot_colorclade_comparison,
            {
                k: alifestd_try_add_ancestor_list_col(v)
                for k, v in frames.items()
            },
            show_fossils=kwargs["fossil_interval"] is not None,
            teeplot_dpi=100,
            teeplot_outattrs=kwargs,
            teeplot_outdir="/tmp/end2end-visualizations",
        )


def test_reconstruct_one(
    differentia_bitwidth: int,
    surface_size: int,
    fossil_interval: typing.Optional[int],
    *,
    visualize: bool,
) -> typing.Dict[str, typing.Union[int, float, None]]:
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

    display_reconstruction(
        frames,
        differentia_bitwidth=differentia_bitwidth,
        surface_size=surface_size,
        fossil_interval=fossil_interval,
        create_plots=visualize,
    )
    reconstruction_error = alifestd_calc_triplet_distance_asexual(
        alifestd_collapse_unifurcations(frames["exact"]), frames["reconst"]
    )

    reconstruction_error_dropped_fossils = (
        alifestd_calc_triplet_distance_asexual(
            alifestd_collapse_unifurcations(frames["exact_dropped_fossils"]),
            frames["reconst_dropped_fossils"],
        )
    )

    print(f"{reconstruction_error=}")
    print(f"{reconstruction_error_dropped_fossils=}")
    assert 0 <= reconstruction_error <= 1  # should be in the range [0,1]

    return {
        "differentia_bitwidth": differentia_bitwidth,
        "surface_size": surface_size,
        "fossil_interval": fossil_interval,
        "error": reconstruction_error,
        "error_dropped_fossils": reconstruction_error_dropped_fossils,
    }


def _parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--skip-visualization", action="store_true")
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
                visualize=not args.skip_visualization,
            )
            for (
                fossil_interval,
                surface_size,
                differentia_bitwidth,
            ) in product((None, 50, 200), (256, 64, 16), (64, 8, 1))
        ]
    ).sort_values(["surface_size", "differentia_bitwidth"], ascending=False)

    reconstruction_errors.to_csv("/tmp/end2end-reconstruction-error.csv")

    # error should increase with decreasing surface size
    tolerance = 0.02
    assert (  # type: ignore
        reconstruction_errors.groupby("fossil_interval", dropna=False)["error"]
        .agg(
            lambda x: (
                x + pd.Series([tolerance] * 9).cumsum().values
            ).is_monotonic_increasing
        )
        .all()
    )
