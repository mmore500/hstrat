from collections import defaultdict
from functools import lru_cache
import typing

from downstream import dsurf
import more_itertools as mit
import opytional as opyt

from hstrat._auxiliary_lib import HereditaryStratigraphicInstrument

from ..._auxiliary_lib import demark
from ...genome_instrumentation import (
    HereditaryStratigraphicColumn,
    HereditaryStratigraphicSurface,
    HereditaryStratum,
    HereditaryStratumOrderedStoreList,
)


def _calc_node_depths(
    descending_tree_iterable: typing.Iterable,
    get_parent: typing.Callable[[typing.Any], typing.Any],
    get_stem_length: typing.Callable[[typing.Any], int],
    demark: typing.Callable[[typing.Any], typing.Hashable] = demark,
    progress_wrap: typing.Callable = lambda x: x,
) -> typing.Dict[int, int]:
    """Descend tree to prepare lookup table of `demark(node)` -> node depth."""

    node_depth_lookup = dict()

    descending_tree_iterator = iter(progress_wrap(descending_tree_iterable))

    for root_node in descending_tree_iterator:
        node_depth_lookup[demark(root_node)] = 0
        break

    for node in descending_tree_iterator:
        stem_length = get_stem_length(node)
        parent_node = get_parent(node)
        node_depth_lookup[demark(node)] = (
            node_depth_lookup[demark(parent_node)] + stem_length
        )

    return node_depth_lookup


def _educe_surface_object(
    seed_surface: HereditaryStratigraphicSurface,
    deposition_count_lookup: typing.Dict[int, int],
    ascending_lineage_iterable: typing.Iterable,
    stem_strata_lookup: typing.Dict[int, typing.Callable[[int], int]],
    demark: typing.Callable[[typing.Any], typing.Hashable] = demark,
) -> HereditaryStratigraphicSurface:
    """Prepare strata required by one extant lineage member, using cache lookup
    to ensure that identical strata are provided where common ancestry is
    shared with previously processed extant lineage members."""

    try:
        extant_node = ascending_lineage_iterable[0]
    except TypeError:
        # usage ensures ascending_lineage_iterable not empty
        (extant_node,), ascending_lineage_iterable = mit.spy(
            ascending_lineage_iterable
        )

    extant_deposition_count = deposition_count_lookup[demark(extant_node)]

    rising_required_ranks_iterator = sorted(
        seed_surface._surface.algo.lookup_ingest_times(
            seed_surface.S,
            extant_deposition_count,
        )
    )

    # pairwise ensures we exclude root node
    storage = [None] * seed_surface.S
    try:
        descending_lineage_iterator = iter(
            reversed(ascending_lineage_iterable)
        )
    except TypeError:
        descending_lineage_iterator = iter(
            reversed([*ascending_lineage_iterable])
        )

    cur_node = next(descending_lineage_iterator)

    for rank in rising_required_ranks_iterator:
        while rank >= deposition_count_lookup[demark(cur_node)]:
            cur_node = next(descending_lineage_iterator)

        rank_stratum_lookup = stem_strata_lookup[demark(cur_node)]
        storage[
            seed_surface._surface.algo.assign_storage_site(
                seed_surface.S, rank
            )
        ] = rank_stratum_lookup(rank - seed_surface.S)

    return HereditaryStratigraphicSurface(
        dsurf.Surface(
            seed_surface._surface.algo, storage, extant_deposition_count
        )
    )


def _educe_stratum_ordered_store(
    ascending_lineage_iterable: typing.Iterable,
    deposition_count_lookup: typing.Dict[typing.Hashable, int],
    stem_strata_lookup: typing.Dict[
        int, typing.Callable[[int], HereditaryStratum]
    ],
    stratum_retention_policy: typing.Any,
    demark: typing.Callable[[typing.Any], typing.Hashable] = demark,
) -> HereditaryStratumOrderedStoreList:
    """Prepare strata required by one extant lineage member, using cache lookup
    to ensure that identical strata are provided where common ancestry is
    shared with previously processed extant lineage members."""

    try:
        extant_node = ascending_lineage_iterable[0]
    except TypeError:
        # usage ensures ascending_lineage_iterable not empty
        (extant_node,), ascending_lineage_iterable = mit.spy(
            ascending_lineage_iterable
        )

    extant_deposition_count = deposition_count_lookup[demark(extant_node)]

    rising_required_ranks_iterator = (
        stratum_retention_policy.IterRetainedRanks(
            extant_deposition_count,
        )
    )

    # pairwise ensures we exclude root node
    stratum_ordered_store = HereditaryStratumOrderedStoreList()
    try:
        descending_lineage_iterator = iter(
            reversed(ascending_lineage_iterable)
        )
    except TypeError:
        descending_lineage_iterator = iter(
            reversed([*ascending_lineage_iterable])
        )

    cur_node = next(descending_lineage_iterator)

    for rank in rising_required_ranks_iterator:
        while rank >= deposition_count_lookup[demark(cur_node)]:
            cur_node = next(descending_lineage_iterator)

        rank_stratum_lookup = stem_strata_lookup[demark(cur_node)]
        stratum_ordered_store.DepositStratum(
            rank=rank,
            stratum=rank_stratum_lookup(rank),
        )

    return stratum_ordered_store, extant_deposition_count


def descend_template_phylogeny_posthoc(
    ascending_lineage_iterables: typing.Iterable[typing.Iterable],
    descending_tree_iterable: typing.Iterable,
    get_parent: typing.Callable[[typing.Any], typing.Any],
    get_stem_length: typing.Callable[[typing.Any], int],
    seed_instrument: HereditaryStratigraphicInstrument,
    demark: typing.Callable[[typing.Any], typing.Hashable] = demark,
    progress_wrap: typing.Callable = lambda x: x,
) -> typing.List[HereditaryStratigraphicInstrument]:
    """Generate a population of hereditary stratigraphic columns that could
    have resulted from the template phylogeny.

    Calculates required ranks according to stratum retention policy for each
    extant lineage member, creating returned columns with strata at those
    ranks. Uses cache lookup to ensure that identical strata are provided where
    extant lineage members share common ancestry.

    Requires `seed_column`'s stratum retention policy to provide
    `IterRetainedRanks()` method.

    Prefer to use `descend_template_phylogeny`, which will automatically
    delegate to posthoc implementation if stratum retention policy requirements
    are met. See `descend_template_phylogeny` for parameter and return value details.
    """

    tree_depth_lookup = _calc_node_depths(
        descending_tree_iterable,
        get_parent,
        get_stem_length,
        progress_wrap=progress_wrap,
        demark=demark,
    )
    deposition_count_lookup = {
        k: v + seed_instrument.GetNumStrataDeposited()
        for k, v in tree_depth_lookup.items()
    }

    if isinstance(seed_instrument, HereditaryStratigraphicColumn):
        stem_strata_lookup = defaultdict(
            # use lru_cache as defaultdict with default factory conditioned on key
            lambda: lru_cache(maxsize=None)(
                lambda rank: (
                    # if applicable, use stratum from seed column
                    # otherwise, create new stratum
                    seed_instrument.GetStratumAtRank(rank)
                    if rank < seed_instrument.GetNumStrataDeposited()
                    else (seed_instrument._CreateStratum(rank))
                )
            )
        )
        stratum_retention_policy = seed_instrument._stratum_retention_policy
        assert stratum_retention_policy.IterRetainedRanks is not None
        return [
            HereditaryStratigraphicColumn(
                always_store_rank_in_stratum=seed_instrument._always_store_rank_in_stratum,
                stratum_retention_policy=stratum_retention_policy,
                stratum_differentia_bit_width=seed_instrument.GetStratumDifferentiaBitWidth(),
                stratum_ordered_store=_educe_stratum_ordered_store(
                    iter_,
                    deposition_count_lookup,
                    stem_strata_lookup,
                    stratum_retention_policy,
                    demark=demark,
                ),
            )
            for iter_ in progress_wrap(ascending_lineage_iterables)
        ]
    elif isinstance(seed_instrument, HereditaryStratigraphicSurface):
        stem_strata_lookup = defaultdict(
            # use lru_cache as defaultdict with default factory conditioned on key
            lambda: lru_cache(maxsize=None)(
                lambda rank: (
                    # if applicable, use stratum from seed column
                    # otherwise, create new stratum
                    opyt.apply_if_or_else(
                        seed_instrument.GetStratumAtRank(rank),
                        lambda x: x._differentia,
                        seed_instrument._CreateStratum,
                    )
                    if rank < seed_instrument.GetNumStrataDeposited()
                    else (seed_instrument._CreateStratum())
                )
            )
        )
        return [
            _educe_surface_object(
                seed_instrument,
                deposition_count_lookup,
                iter_,
                stem_strata_lookup,
                demark=demark,
            )
            for iter_ in progress_wrap(ascending_lineage_iterables)
        ]
    raise ValueError(
        "`return_type` must be one of `HereditaryStratigraphicSurface` or `HereditaryStratigraphicColumn`"
    )
