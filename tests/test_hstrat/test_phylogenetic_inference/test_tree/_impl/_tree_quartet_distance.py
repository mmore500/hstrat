import alifedata_phyloinformatics_convert as apc
import tqdist


def tree_quartet_distance(x, y) -> float:
    tree_a = apc.RosettaTree(x).as_dendropy
    tree_b = apc.RosettaTree(y).as_dendropy

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

    return tqdist.quartet_distance(
        tree_a.as_string(schema="newick").strip(),
        tree_b.as_string(schema="newick").strip(),
    )
