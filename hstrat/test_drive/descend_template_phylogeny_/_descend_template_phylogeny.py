import typing

from ..._auxiliary_lib import demark
from ...genome_instrumentation import HereditaryStratigraphicColumn
from ._descend_template_phylogeny_naive import descend_template_phylogeny_naive
from ._descend_template_phylogeny_posthoc import (
    descend_template_phylogeny_posthoc,
)


def descend_template_phylogeny(
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

    Parameters
    ----------
    ascending_lineage_iterables : iterable of phylogeny node iterables
        Iterable that yields an acending lineage iterable for each extant
        individual from template phylogeny.

        The acending lineage iterable should yield the extant individual's
        phylogeny node object and then successive parent node objects until
        yielding the root node object.
    descending_tree_iterable : iterable of phylogeny nodes
        Iterable over all phylogeny node objects in template phylogeny.

        The root node object must be yielded first. Then, each phylogeny node
        object should be yielded, with no object being yielded before its
        parent object. Any topologically sorted ordering is allowed, including
        pre-order depth-first iteration and breadth-first (a.k.a. level-order)
        iteration.
    get_parent : function
        Function that returns the parent node object for a phylogeny node
        object.

        Will never be called on root node object.
    get_stem_length : function
        Function that returns the length of the subtending edge for a phylogeny
        node.

        Length should be an integer value representing the number of
        generations elapsed between the focal node's parent and the focal node.
        Will never be called on root node object.

        For phylogenies including all ancestors as distinct nodes, `lambda
        node: 1` can be specified.
    seed_column : HereditaryStratigraphicColumn
        Hereditary stratigraphic column to seed at root node of phylogeny.

        Returned hereditary stratigraphic column population will be generated
        as if repeatedly calling `CloneDescendant()` on `seed_column`. As such,
        specifies configuration (i.e., differentia bit width and stratum
        retention policy) for returned columns. May already have strata
        deposited, which will be incorporated into generated extant population.
    demark : function, default _auxiliary_lib.demark
        Function that converts returned nodes to a unique hashable value.

        For object-based Nodes, this might be `id`. For value-based Nodes, this
        might be an identity function.

        If default, will use runtime type information to make a reasonable
        guess. Passing a custom value allows bypass of this slow type
        inspection.
    progress_wrap : Callable, default identity function
        Wrapper applied around generation iterator and row generator for final
        phylogeny compilation process.

        Pass tqdm or equivalent to display progress bars.

    Returns
    -------
    list of HereditaryStratigraphicColumn
        Population of hereditary stratigraphic columns for extant lineage
        members.

        Order of columns corresponds to order of `ascending_lineage_iterables`.

    Notes
    -----
    To improve performance, consider preprocessing template phylogeny
    representation to collapse unifurcation chains (i.e., converting chains of
    `n` nodes to a single node with stem length `n`).

    Delegates to `descend_template_phylogeny_naive` or
    `descend_template_phylogeny_posthoc`, depending on whether retained ranks
    at an arbitrary generation can be calculated by the `seed_column`'s stratum
    retention policy.
    """

    impl = (
        descend_template_phylogeny_posthoc
        if seed_column._stratum_retention_policy.IterRetainedRanks is not None
        else descend_template_phylogeny_naive
    )

    return impl(
        ascending_lineage_iterables,
        descending_tree_iterable,
        get_parent,
        get_stem_length,
        seed_column,
        demark=demark,
        progress_wrap=progress_wrap,
    )
