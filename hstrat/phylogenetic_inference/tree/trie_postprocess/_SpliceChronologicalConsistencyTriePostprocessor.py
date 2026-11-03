import logging
import typing

from phyloframe import legacy as pfl
import polars as pl

from ...._auxiliary_lib import log_context_duration, warn_experimental
from ._detail import TriePostprocessorBase


def _fill_spliced_nodes(trie: pl.DataFrame, num_original: int) -> pl.DataFrame:
    """Sort spliced-in nodes topologically, with contiguous ids, and fill
    their `rank` and uniform hstrat metadata columns."""
    trie = trie.with_columns(
        pl.col(col).fill_null(pl.col(col).head(num_original).first())
        for col in ("dstream_S", "hstrat_differentia_bitwidth")
        if col in trie.columns
    )
    trie = pfl.alifestd_assign_contiguous_ids_polars(
        pfl.alifestd_topological_sort_polars(trie),
    )
    if "rank" not in trie.columns:
        return trie

    # spliced nodes take nearest original ancestor's rank, as trie ranks
    # increase along lineages; spliced roots take their clade's min rank
    ranked = trie.select(pl.col("id", "ancestor_id").cast(pl.Int64), "rank")
    ranked = pfl.alifestd_mark_lineage_ffill_polars(
        ranked, "rank", mark_as="_ancestor_rank"
    )
    ranked = pfl.alifestd_mark_lineage_cummin_polars(
        ranked, "rank", reverse=True, mark_as="_clade_rank"
    )
    filled_rank = ranked.select(
        pl.coalesce("_ancestor_rank", "_clade_rank").cast(trie.schema["rank"]),
    ).to_series()
    return trie.with_columns(rank=filled_rank)


def _call_polars(
    ftor: "SpliceChronologicalConsistencyTriePostprocessor",
    trie: pl.DataFrame,
) -> pl.DataFrame:
    """Implementation detail."""
    if not pfl.alifestd_has_contiguous_ids_polars(trie):
        raise NotImplementedError("non-contiguous ids not supported")
    if not pfl.alifestd_is_topologically_sorted_polars(trie):
        raise NotImplementedError("non-topologically-sorted not supported")

    num_original = trie.lazy().select(pl.len()).collect().item()
    property_ = ftor._origin_time_property
    displaced = "_splice_chronological_consistency_origin_time"
    renames = (
        {}
        if property_ == "origin_time"
        else {
            **(
                {"origin_time": displaced}
                if "origin_time" in trie.columns
                else {}
            ),
            property_: "origin_time",
        }
    )
    with log_context_duration(
        "alifestd_splice_chronological_consistency_polars", logging.info
    ):
        trie = pfl.alifestd_splice_chronological_consistency_polars(
            trie.rename(renames),
        )
    assert pfl.alifestd_find_chronological_inconsistency_polars(trie) is None
    trie = trie.rename({v: k for k, v in renames.items()})

    if trie.lazy().select(pl.len()).collect().item() == num_original:
        return trie  # nothing spliced
    return _fill_spliced_nodes(trie, num_original)


@warn_experimental
class SpliceChronologicalConsistencyTriePostprocessor(TriePostprocessorBase):
    """Functor to resolve trie nodes with origin times preceding their
    parent's by adjusting topology, leaving origin times unchanged.

    Each such node is reattached, with its subtree, onto a new node spliced
    into its lineage where it passes through the node's origin time, via
    phyloframe's `alifestd_splice_chronological_consistency_polars`. So, the
    node remains grouped with the clade it originally belonged to, as sister
    to it. Nodes preceding their entire lineage are reattached onto a new
    root spliced above it, so the number of roots is unchanged.

    Spliced nodes take the origin time of the node they are spliced for.
    They take the `rank` of their nearest ancestor (or, for spliced roots,
    the minimum `rank` in their clade), and `dstream_S` and
    `hstrat_differentia_bitwidth` are filled with their uniform values.
    Other columns are null for spliced nodes. If any nodes are spliced, ids
    are reassigned to keep the trie topologically sorted and contiguous.

    Use after a postprocessor that assigns origin times, e.g., to resolve
    negative branch lengths from
    `AssignOriginTimeGeometricSurfPostprocessor`, via
    `CompoundTriePostprocessor`.

    Notes
    -----
    Only polars dataframe tries are supported (e.g., via
    `surface_postprocess_trie`).

    Examples
    --------
    >>> hstrat.dataframe.surface_build_tree(
    ...     df,
    ...     trie_postprocessor=hstrat.CompoundTriePostprocessor(
    ...         [
    ...             hstrat.AssignOriginTimeGeometricSurfPostprocessor(
    ...                 "dstream.steady_algo",
    ...             ),
    ...             hstrat.SpliceChronologicalConsistencyTriePostprocessor(),
    ...         ],
    ...     ),
    ... )
    """

    _origin_time_property: str  # property name for origin time

    def __init__(
        self: "SpliceChronologicalConsistencyTriePostprocessor",
        origin_time_property: str = "origin_time",
    ) -> None:
        """Initialize functor instance.

        Parameters
        ----------
        origin_time_property : str, default "origin_time"
            Property name for origin time.
        """
        self._origin_time_property = origin_time_property

    def __call__(
        self: "SpliceChronologicalConsistencyTriePostprocessor",
        trie: pl.DataFrame,
        p_differentia_collision: float,  # noqa: ARG002
        mutate: bool = False,  # noqa: ARG002
        progress_wrap: typing.Callable = lambda x: x,  # noqa: ARG002
    ) -> pl.DataFrame:
        """Splice in nodes to resolve origin time inversions.

        Parameters
        ----------
        trie : pl.DataFrame
            The input trie to be postprocessed.

            Only polars dataframe tries are supported; other types raise
            `NotImplementedError`. Tries must have contiguous ids, be
            topologically sorted, and provide an origin time column.
        p_differentia_collision : float
            Probability of a randomly-generated differentia matching an
            existing differentia.

            Not used.
        mutate : bool, default False
            Are side effects on the input argument `trie` allowed?

            Not used, as polars operations don't modify their input.
        progress_wrap : typing.Callable, optional
            Pass tqdm or equivalent to report progress.

            Not used in the current implementation.

        Returns
        -------
        pl.DataFrame
            The postprocessed trie, without origin time inversions.
        """
        if not isinstance(trie, pl.DataFrame):
            raise NotImplementedError(
                f"{type(trie)} tries are not supported; use polars "
                "dataframe tries (e.g., surface_postprocess_trie)",
            )
        return _call_polars(self, trie)
