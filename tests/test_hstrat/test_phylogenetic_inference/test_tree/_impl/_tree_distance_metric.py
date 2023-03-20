import alifedata_phyloinformatics_convert as apc
import dendropy as dp
from iterpop import iterpop as ip


def tree_distance_metric(x, y) -> float:
    tree_a = apc.RosettaTree(x).as_dendropy
    tree_b = apc.RosettaTree(y).as_dendropy

    common_namespace = dp.TaxonNamespace()
    tree_a.migrate_taxon_namespace(common_namespace)
    tree_b.migrate_taxon_namespace(common_namespace)

    tree_a.encode_bipartitions()
    for bp in tree_a.bipartition_encoding:
        bp.is_mutable = False
    tree_b.encode_bipartitions()
    for bp in tree_b.bipartition_encoding:
        bp.is_mutable = False

    # see https://rdrr.io/cran/phangorn/man/treedist.html
    estimated_max_rf_dist = (
        2
        * ip.pophomogeneous(
            (len(tree_a.leaf_nodes()), len(tree_b.leaf_nodes()))
        )
        - 6
    )

    return (
        dp.calculate.treecompare.symmetric_difference(
            tree_a, tree_b, is_bipartitions_updated=True
        )
        / estimated_max_rf_dist
    )
