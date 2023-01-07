import typing

from ..genome_instrumentation import HereditaryStratigraphicColumn


def descend_template_phylogeny_naive(
    ascending_lineage_iterators: typing.Iterator[typing.Iterator],
    descending_tree_iterator: typing.Iterator,
    get_parent: typing.Callable,
    get_stem_length: typing.Callable,
    seed_column: HereditaryStratigraphicColumn,
) -> typing.List[HereditaryStratigraphicColumn]:

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
        hstrat_column_lookup[id(next(ascending_lineage_iterator))]  # tip node
        for ascending_lineage_iterator in ascending_lineage_iterators
    ]
    return extant_population
