#!/bin/bash

set -euo pipefail

cd "$(dirname "$0")"

for differentia_bitwidth in 64 8 1; do

python3 <<EOF
import os
import subprocess
import typing

import alifedata_phyloinformatics_convert as apc
import dendropy as dp
from hstrat._auxiliary_lib import (
    alifestd_collapse_unifurcations,
    alifestd_count_leaf_nodes,
    alifestd_prune_extinct_lineages_asexual,
    alifestd_try_add_ancestor_id_col,
    alifestd_try_add_ancestor_list_col,
)
import numpy as np
import pandas as pd

try:
    import tqdist
except (ImportError, ModuleNotFoundError) as e:
    print("tqdist required for dstream surf evolution example")
    print("python3 -m pip install tqdist")
    raise e


# adapted from https://github.com/mmore500/hstrat/blob/d23917cf03ba59061ff2f9b951efe79e995eb4d8/tests/test_hstrat/test_phylogenetic_inference/test_tree/_impl/_tree_quartet_distance.py
def calc_triplet_distance(ref: pd.DataFrame, cmp: pd.DataFrame) -> float:
    """Calculate the triplet distance between two trees."""
    tree_a = apc.RosettaTree(ref).as_dendropy
    tree_b = apc.RosettaTree(cmp).as_dendropy

    # must suppress root unifurcations or tqdist barfs
    # see https://github.com/uym2/tripVote/issues/15
    tree_a.unassign_taxa(exclude_leaves=True)
    tree_a.suppress_unifurcations()
    tree_b.unassign_taxa(exclude_leaves=True)
    tree_b.suppress_unifurcations()

    tree_a_taxon_labels = [
        leaf.taxon.label for leaf in tree_a.leaf_node_iter()
    ]
    tree_b_taxon_labels = [
        leaf.taxon.label for leaf in tree_b.leaf_node_iter()
    ]
    assert {*tree_a_taxon_labels} == {*tree_b_taxon_labels}
    for taxon_label in tree_a_taxon_labels:
        assert taxon_label
        assert taxon_label.strip()

    return tqdist.triplet_distance(
        tree_a.as_string(schema="newick").removeprefix("[&R]").strip(),
        tree_b.as_string(schema="newick").removeprefix("[&R]").strip(),
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
    surface_size: int
) -> typing.Tuple[pd.DataFrame, pd.DataFrame]:
    """Sample a reference phylogeny and corresponding reconstruction."""
    paths = subprocess.run(
        [
            "./end2end_tree_reconstruction_with_dstream_surf.sh",
            "--differentia-bitwidth",
            "${differentia_bitwidth}",
            "--surface-size",
            f"{surface_size}",
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

    assert (
        alifestd_count_leaf_nodes(true_phylo_df)
        == alifestd_count_leaf_nodes(reconst_phylo_df)
    )

    return true_phylo_df, reconst_phylo_df


def visualize_reconstruction(
    true_phylo_df: pd.DataFrame, reconst_phylo_df: pd.DataFrame
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


def test_reconstruct_one(surface_size: int) -> float:
    """Test the reconstruction of a single phylogeny."""
    print("=" * 80)
    print(f"surface_size: {surface_size}")
    print("differentia_bitwidth: ${differentia_bitwidth}")

    true_phylo_df, reconst_phylo_df = sample_reference_and_reconstruction(
        surface_size
    )

    visualize_reconstruction(true_phylo_df, reconst_phylo_df)
    reconstruction_error = calc_triplet_distance(
        alifestd_collapse_unifurcations(true_phylo_df), reconst_phylo_df
    )
    print(f"{reconstruction_error=}")
    assert reconstruction_error < alifestd_count_leaf_nodes(true_phylo_df)

    return reconstruction_error


if __name__ == "__main__":
    reconstruction_errors = [
        test_reconstruct_one(surface_size) for surface_size in (256, 64, 16)
    ]
    # error should increase with decreasing surface size
    assert sorted(reconstruction_errors) == reconstruction_errors

EOF

done  # for differentia_bitwidth in 1 8 64; do

echo "$0 All tests passed!"
