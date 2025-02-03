#!/usr/bin/env python3

import os
import subprocess
import typing

import alifedata_phyloinformatics_convert as apc
import pandas as pd

from hstrat._auxiliary_lib import (
    alifestd_calc_triplet_distance_asexual,
    alifestd_collapse_unifurcations,
    alifestd_count_leaf_nodes,
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
) -> typing.Tuple[pd.DataFrame, pd.DataFrame]:
    """Sample a reference phylogeny and corresponding reconstruction."""
    paths = subprocess.run(
        [
            "./end2end_tree_reconstruction_with_dstream_surf.sh",
            "--skip-visualization",
            "--differentia-bitwidth",
            f"{differentia_bitwidth}",
            "--surface-size",
            f"{surface_size}",
        ]
        + (
            ["--fossil-interval", f"{fossil_interval}"]
            if fossil_interval is not None
            else []
        ),
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


def test_reconstruct_one(
    differentia_bitwidth: int,
    surface_size: int,
    fossil_interval: typing.Optional[int],
) -> float:
    """Test the reconstruction of a single phylogeny."""
    print("=" * 80)
    print(f"surface_size: {surface_size}")
    print(f"differentia_bitwidth: {differentia_bitwidth}")
    print(f"fossil_interval: {fossil_interval}")

    true_phylo_df, reconst_phylo_df = sample_reference_and_reconstruction(
        differentia_bitwidth,
        surface_size,
        fossil_interval,
    )

    visualize_reconstruction(true_phylo_df, reconst_phylo_df)
    reconstruction_error = alifestd_calc_triplet_distance_asexual(
        alifestd_collapse_unifurcations(true_phylo_df), reconst_phylo_df
    )
    print(f"{reconstruction_error=}")
    assert reconstruction_error < alifestd_count_leaf_nodes(true_phylo_df)

    return reconstruction_error


if __name__ == "__main__":
    reconstruction_errors = [
        test_reconstruct_one(
            differentia_bitwidth, surface_size, fossil_interval
        )
        for fossil_interval in (None, 50, 200)
        for surface_size in (256, 64, 16)
        for differentia_bitwidth in (64, 8, 1)
    ]
    # error should increase with decreasing surface size
    assert all(
        sorted(reconstruction_errors[i : i + 9])
        == reconstruction_errors[i : i + 9]
        for i in range(3)
    )
