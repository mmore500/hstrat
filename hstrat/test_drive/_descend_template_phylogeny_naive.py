import typing

from ..genome_instrumentation import HereditaryStratigraphicColumn


def descend_template_phylogeny_naive(
    ascending_lineage_iterators: typing.Iterator[typing.Iterator],
    descending_tree_iterator: typing.Iterator,
    get_parent: typing.Callable[[typing.Any], typing.Any],
    get_stem_length: typing.Callable[[typing.Any], int],
    seed_column: HereditaryStratigraphicColumn,
) -> typing.List[HereditaryStratigraphicColumn]:
    """Generate a population of hereditary stratigraphic columns that could
    have resulted from the template phylogeny.

    Traverses phylogenetic tree in topological order, generating a clone column
    with `get_stem_length(node)` additional stratum deposits for each node
    (including internal nodes). Uses `CloneNthDescendant()` instead of `n`
    calls to `CloneDescendant()` to improve efficiency where
    `get_stem_length(node)` > 1.

    prefer to use `descend_template_phylogeny`, which will automatically
    delegate between naive and posthoc implementation, unless performance
    considerations merit manual override.
    """

    hstrat_column_lookup = dict()  # node id -> column

    for root_node in descending_tree_iterator:
        hstrat_column_lookup[id(root_node)] = seed_column
        break

    for node in descending_tree_iterator:
        stem_length = get_stem_length(node)
        parent_node = get_parent(node)
        parent_hstrat_column = hstrat_column_lookup[id(parent_node)]

        node_hstrat_column = parent_hstrat_column.CloneNthDescendant(
            stem_length
        )
        hstrat_column_lookup[id(node)] = node_hstrat_column

    extant_population = [
        # extant node
        hstrat_column_lookup[id(next(ascending_lineage_iterator))]
        for ascending_lineage_iterator in ascending_lineage_iterators
    ]
    return extant_population
