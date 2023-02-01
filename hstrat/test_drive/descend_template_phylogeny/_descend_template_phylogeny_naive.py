import typing

from ..._auxiliary_lib import demark
from ...genome_instrumentation import HereditaryStratigraphicColumn


def descend_template_phylogeny_naive(
    ascending_lineage_iterables: typing.Iterable[typing.Iterable],
    descending_tree_iterable: typing.Iterable,
    get_parent: typing.Callable[[typing.Any], typing.Any],
    get_stem_length: typing.Callable[[typing.Any], int],
    seed_column: HereditaryStratigraphicColumn,
    demark: typing.Callable[[typing.Any], typing.Hashable] = demark,
    progress_wrap: typing.Callable = lambda x: x,
) -> typing.List[HereditaryStratigraphicColumn]:
    """Generate a population of hereditary stratigraphic columns that could
    have resulted from the template phylogeny.

    Traverses phylogenetic tree in topological order, generating a clone column
    with `get_stem_length(node)` additional stratum deposits for each node
    (including internal nodes). Uses `CloneNthDescendant()` instead of `n`
    calls to `CloneDescendant()` to improve efficiency where
    `get_stem_length(node)` > 1.

    Prefer to use `descend_template_phylogeny`, which will automatically
    delegate between naive and posthoc implementation, unless performance
    considerations merit manual override.
    """

    hstrat_column_lookup = dict()  # node id -> column

    descending_tree_iterator = iter(descending_tree_iterable)

    for root_node in descending_tree_iterator:
        hstrat_column_lookup[demark(root_node)] = seed_column
        break

    for node in progress_wrap(descending_tree_iterator):
        stem_length = get_stem_length(node)
        parent_node = get_parent(node)
        parent_hstrat_column = hstrat_column_lookup[demark(parent_node)]

        node_hstrat_column = parent_hstrat_column.CloneNthDescendant(
            stem_length
        )
        hstrat_column_lookup[demark(node)] = node_hstrat_column

    extant_population = [
        # extant node
        hstrat_column_lookup[demark(next(iter(ascending_lineage_iterable)))]
        for ascending_lineage_iterable in ascending_lineage_iterables
    ]
    return extant_population
