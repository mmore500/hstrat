import pandas as pd
import tqdist

from . import (
    alifestd_as_newick_asexual,
    alifestd_collapse_unifurcations,
    alifestd_count_root_nodes,
    alifestd_mark_leaves,
)


# adapted from https://github.com/mmore500/hstrat/blob/d23917cf03ba59061ff2f9b951efe79e995eb4d8/tests/test_hstrat/test_phylogenetic_inference/test_tree/_impl/_tree_quartet_distance.py
def alifestd_calc_triplet_distance_asexual(
    ref: pd.DataFrame,
    cmp: pd.DataFrame,
    taxon_label_key: str = "taxon_label",
) -> float:
    """Calculate the triplet distance between two trees."""

    ref = alifestd_mark_leaves(alifestd_collapse_unifurcations(ref))
    cmp = alifestd_mark_leaves(alifestd_collapse_unifurcations(cmp))

    ref.loc[~ref["is_leaf"], taxon_label_key] = ""
    cmp.loc[~cmp["is_leaf"], taxon_label_key] = ""

    ref_labels = {*ref[taxon_label_key][ref["is_leaf"]]}
    cmp_labels = {*cmp[taxon_label_key][cmp["is_leaf"]]}

    if ref_labels != cmp_labels:
        raise ValueError("Taxon labels must match between trees")
    for taxon_label in ref_labels:
        if isinstance(taxon_label, str) and not taxon_label.strip():
            raise ValueError("Cannot have empty taxon labels")

    if (
        alifestd_count_root_nodes(ref) > 1
        or alifestd_count_root_nodes(cmp) > 1
    ):
        raise ValueError(
            f"Cannot have disjunct trees in `{alifestd_calc_triplet_distance_asexual.__name__}`"
        )

    ref_newick = (
        alifestd_as_newick_asexual(ref, taxon_label=taxon_label_key)
        .removeprefix("[&R]")
        .strip()
    )
    cmp_newick = (
        alifestd_as_newick_asexual(cmp, taxon_label=taxon_label_key)
        .removeprefix("[&R]")
        .strip()
    )
    return tqdist.triplet_distance(ref_newick, cmp_newick)
