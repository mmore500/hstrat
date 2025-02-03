import alifedata_phyloinformatics_convert as apc
import pandas as pd
import tqdist

# adapted from https://github.com/mmore500/hstrat/blob/d23917cf03ba59061ff2f9b951efe79e995eb4d8/tests/test_hstrat/test_phylogenetic_inference/test_tree/_impl/_tree_quartet_distance.py
def alifestd_calc_triplet_distance_asexual(ref: pd.DataFrame, cmp: pd.DataFrame) -> float:
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

