import typing

from ..genome_instrumentation import HereditaryStratigraphicColumn
from ._descend_template_phylogeny_naive import descend_template_phylogeny_naive
from ._descend_template_phylogeny_posthoc import (
    descend_template_phylogeny_posthoc,
)


def descend_template_phylogeny(
    ascending_lineage_iterators: typing.Iterator[typing.Iterator],
    descending_tree_iterator: typing.Iterator,
    get_parent: typing.Callable,
    get_stem_length: typing.Callable,
    seed_column: HereditaryStratigraphicColumn,
) -> typing.List[HereditaryStratigraphicColumn]:

    impl = (
        descend_template_phylogeny_posthoc
        if seed_column._stratum_retention_policy.IterRetainedRanks is not None
        else descend_template_phylogeny_naive
    )

    return impl(
        ascending_lineage_iterators,
        descending_tree_iterator,
        get_parent,
        get_stem_length,
        seed_column,
    )
