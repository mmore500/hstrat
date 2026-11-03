import os

import numpy as np
from phyloframe import legacy as pfl
import polars as pl
import pytest

from hstrat import hstrat
from hstrat._auxiliary_lib import ExperimentalWarning, seed_random
from hstrat.dataframe import surface_build_tree, surface_test_drive

assets = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "../../../test_dataframe/assets",
)


def _count_inversions(
    phylo: pl.DataFrame, origin_time_property: str = "origin_time"
) -> int:
    """Number of non-root nodes with origin time preceding their parent's."""
    ancestors = phylo["ancestor_id"].to_numpy().astype(np.int64)
    times = phylo[origin_time_property].to_numpy()
    is_root = ancestors == np.arange(len(ancestors))
    return int((~is_root & (times < times[ancestors])).sum())


def _make_trie(origin_time_property: str = "origin_time") -> pl.DataFrame:
    # root <- inner (34.5) <- inner (33.5) <- two leaves; and another leaf
    return pl.DataFrame(
        {
            "id": [0, 1, 2, 3, 4, 5],
            "ancestor_id": [0, 0, 1, 2, 2, 1],
            "rank": [64, 100, 99, 199, 199, 199],
            "dstream_S": [64] * 6,
            "hstrat_differentia_bitwidth": [1] * 6,
            origin_time_property: [0.0, 34.5, 33.5, 135.0, 135.0, 135.0],
        },
    )


def test_splice():
    spliced = hstrat.SpliceChronologicalConsistencyTriePostprocessor()(
        _make_trie(), p_differentia_collision=0.5
    )
    # inner node 2 precedes its parent, so is spliced, as sister to its
    # former parent, onto new node 1
    assert spliced["ancestor_id"].to_list() == [0, 0, 1, 1, 2, 3, 3]
    assert spliced["origin_time"].to_list() == [
        0.0,
        33.5,
        34.5,
        33.5,
        135.0,
        135.0,
        135.0,
    ]
    # spliced node takes ancestor's rank and uniform metadata
    assert spliced["rank"].to_list() == [64, 64, 100, 99, 199, 199, 199]
    assert spliced["dstream_S"].to_list() == [64] * 7
    assert spliced["hstrat_differentia_bitwidth"].to_list() == [1] * 7
    assert _count_inversions(spliced) == 0
    assert pfl.alifestd_is_topologically_sorted_polars(spliced)
    assert pfl.alifestd_has_contiguous_ids_polars(spliced)


def test_splice_origin_time_property():
    trie = _make_trie("foo").with_columns(origin_time=pl.lit(-1.0))
    spliced = hstrat.SpliceChronologicalConsistencyTriePostprocessor(
        "foo",
    )(trie, p_differentia_collision=0.5)
    assert spliced["ancestor_id"].to_list() == [0, 0, 1, 1, 2, 3, 3]
    assert _count_inversions(spliced, "foo") == 0
    # existing origin_time column is untouched, null for spliced node
    assert spliced["origin_time"].to_list() == [-1.0, None] + [-1.0] * 5


@pytest.mark.parametrize("id_dtype", [pl.Int64, pl.UInt64])
def test_splice_root(id_dtype: pl.DataType):
    # unifurcating root (0.0) <- inner (-1.5) <- two leaves
    trie = pl.DataFrame(
        {
            "id": [0, 1, 2, 3],
            "ancestor_id": [0, 0, 1, 1],
            "rank": [64, 65, 199, 199],
            "dstream_S": [64] * 4,
            "origin_time": [0.0, -1.5, 135.0, 135.0],
        },
    ).cast({"id": id_dtype, "ancestor_id": id_dtype})
    spliced = hstrat.SpliceChronologicalConsistencyTriePostprocessor()(
        trie, p_differentia_collision=0.5
    )
    # inner node is spliced onto new root, with former root as sister
    assert _count_inversions(spliced) == 0
    roots = spliced.filter(pl.col("id") == pl.col("ancestor_id"))
    assert len(roots) == 1
    assert roots["origin_time"].item() == -1.5
    assert roots["rank"].item() == 64
    assert (spliced["ancestor_id"] == roots["id"].item()).sum() == 3


def test_nothing_to_splice():
    trie = _make_trie().with_columns(
        origin_time=pl.Series([0.0, 33.5, 34.5, 135.0, 135.0, 135.0]),
    )
    assert hstrat.SpliceChronologicalConsistencyTriePostprocessor()(
        trie, p_differentia_collision=0.5
    ).equals(trie)


def test_polars_only():
    with pytest.raises(NotImplementedError):
        hstrat.SpliceChronologicalConsistencyTriePostprocessor()(
            _make_trie().to_pandas(), p_differentia_collision=0.5
        )


@pytest.mark.parametrize(
    "dstream_algo", ["dstream.steady_algo", "dstream.tilted_algo"]
)
@pytest.mark.parametrize("bitwidth", [1, 8])
def test_after_unbiased(dstream_algo: str, bitwidth: int):
    pop = surface_test_drive(
        pl.read_csv(f"{assets}/nk_ecoeaselection.csv"),
        dstream_algo=dstream_algo,
        dstream_S=64,
        stratum_differentia_bit_width=bitwidth,
    )
    unbiased = hstrat.AssignOriginTimeUnbiasedSurfPostprocessor()
    unspliced = surface_build_tree(pop, trie_postprocessor=unbiased)
    spliced = surface_build_tree(
        pop,
        trie_postprocessor=hstrat.CompoundTriePostprocessor(
            [
                unbiased,
                hstrat.SpliceChronologicalConsistencyTriePostprocessor(),
            ],
        ),
    )

    assert _count_inversions(spliced) == 0
    assert pfl.alifestd_is_topologically_sorted_polars(spliced)
    assert pfl.alifestd_has_contiguous_ids_polars(spliced)
    assert spliced["hstrat_rank"].null_count() == 0
    # splicing only adds nodes, with origin times of existing nodes
    assert len(spliced) >= len(unspliced)
    assert {*spliced["origin_time"]} == {*unspliced["origin_time"]}
    leaf_cols = ["dstream_data_id", "origin_time", "hstrat_rank"]
    assert (
        spliced.filter(pl.col("dstream_data_id").is_not_null())
        .select(leaf_cols)
        .sort("dstream_data_id")
        .equals(
            unspliced.filter(pl.col("dstream_data_id").is_not_null())
            .select(leaf_cols)
            .sort("dstream_data_id"),
        )
    )


def _make_nonultrametric_tree(rng: np.random.Generator) -> pl.DataFrame:
    """Random tree: uniform split times, each splitting a random open
    lineage; tips sampled between their parent's split and generation G."""
    n, G = 50, 300
    ids, ancestors, times, open_ = [0], [0], [0], [0]
    for t in np.sort(rng.integers(1, G - 1, size=n - 1)):
        k = rng.integers(len(open_))
        node = len(ids)
        ids.append(node), ancestors.append(open_[k]), times.append(int(t))
        open_[k : k + 1] = [node, node]
    for parent in open_:
        t = int(rng.integers(times[parent] + 1, G + 1))
        ids.append(len(ids)), ancestors.append(parent), times.append(t)
    return pl.DataFrame(
        {"id": ids, "ancestor_id": ancestors, "origin_time": times},
    ).cast(pl.UInt64)


def test_after_unbiased_with_inversions():
    seed_random(1)
    rng = np.random.default_rng(1)
    unbiased = hstrat.AssignOriginTimeUnbiasedSurfPostprocessor()
    for __ in range(50):  # find reconstruction with origin time inversions
        pop = surface_test_drive(
            _make_nonultrametric_tree(rng).lazy(),
            dstream_algo="dstream.steady_algo",
            dstream_S=16,
            stratum_differentia_bit_width=1,
        )
        unspliced = surface_build_tree(pop, trie_postprocessor=unbiased)
        if _count_inversions(unspliced):
            break
    else:
        pytest.fail("no reconstruction with origin time inversions found")

    spliced = surface_build_tree(
        pop,
        trie_postprocessor=hstrat.CompoundTriePostprocessor(
            [
                unbiased,
                hstrat.SpliceChronologicalConsistencyTriePostprocessor(),
            ],
        ),
    )
    assert _count_inversions(spliced) == 0
    assert len(spliced) > len(unspliced)
    assert pfl.alifestd_is_topologically_sorted_polars(spliced)
    assert pfl.alifestd_has_contiguous_ids_polars(spliced)
    assert spliced["hstrat_rank"].null_count() == 0
    assert {*spliced["origin_time"]} == {*unspliced["origin_time"]}


def test_experimental_warning(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.delenv("HSTRAT_WARN_EXPERIMENTAL_SUPPRESS", raising=False)
    with pytest.warns(ExperimentalWarning):
        hstrat.SpliceChronologicalConsistencyTriePostprocessor()
