import alifedata_phyloinformatics_convert as apc
import dendropy as dp


def tree_unweighted_robinson_foulds_distance(x: object, y: object) -> float:
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

    return dp.calculate.treecompare.unweighted_robinson_foulds_distance(
        tree_a, tree_b, is_bipartitions_updated=True
    )
