import os

from downstream import dstream, dsurf
from phyloframe import legacy as pfl
import polars as pl
import pytest

from hstrat import hstrat
from hstrat.dataframe import (
    surface_postprocess_trie,
    surface_unpack_reconstruct,
)
from hstrat.phylogenetic_inference.tree.trie_postprocess import (
    AssignOriginTimeNodeRankTriePostprocessor,
)

assets_path = os.path.join(os.path.dirname(__file__), "assets")


def test_smoke():
    df = pl.read_csv(f"{assets_path}/packed.csv")
    raw = surface_unpack_reconstruct(df)
    res = surface_postprocess_trie(
        raw,
        trie_postprocessor=AssignOriginTimeNodeRankTriePostprocessor(
            t0="dstream_S",
        ),
    )
    assert "origin_time" in res.columns
    assert len(res) <= len(raw)
    assert pfl.alifestd_validate(
        pfl.alifestd_try_add_ancestor_list_col(res.to_pandas()),
    )
    assert pfl.alifestd_is_chronologically_ordered(res.to_pandas())


def test_dstream_rank_in_unpack_reconstruct():
    """dstream_rank should be present after surface_unpack_reconstruct."""
    df = pl.read_csv(f"{assets_path}/packed.csv")
    raw = surface_unpack_reconstruct(df)
    assert "dstream_rank" in raw.columns


def test_smoke_drop_dstream_metadata_false():
    """Smoke test: drop_dstream_metadata=False retains dstream_rank and
    dstream_S."""
    df = pl.read_csv(f"{assets_path}/packed.csv")
    raw = surface_unpack_reconstruct(df)
    res = surface_postprocess_trie(
        raw,
        drop_dstream_metadata=False,
        trie_postprocessor=AssignOriginTimeNodeRankTriePostprocessor(
            t0="dstream_S",
        ),
    )
    assert "dstream_rank" in res.columns
    assert "dstream_S" in res.columns
    assert "hstrat_differentia_bitwidth" in res.columns
    assert len(res) > 0
    assert pfl.alifestd_validate(
        pfl.alifestd_try_add_ancestor_list_col(res.to_pandas()),
    )


def test_drop_dstream_metadata_default_drops_rank_and_S():
    """Default behavior should drop dstream_rank, dstream_S, and
    hstrat_differentia_bitwidth."""
    df = pl.read_csv(f"{assets_path}/packed.csv")
    raw = surface_unpack_reconstruct(df)
    res = surface_postprocess_trie(raw)
    assert "dstream_rank" not in res.columns
    assert "dstream_S" not in res.columns
    assert "hstrat_differentia_bitwidth" not in res.columns


def test_zero_generations_elapsed():
    """Postprocessing should handle surfaces with zero generations elapsed.

    When dstream_T == dstream_S, no generations have elapsed beyond the
    founding ancestor's initial surface fill. This should not cause errors
    or produce an empty result.
    """
    S = 8
    differentia_bitwidth = 8
    dstream_T_bitwidth = 8
    algo = dstream.steady_algo

    # Create surfaces where dstream_T == dstream_S (zero generations elapsed)
    surfaces = [
        hstrat.HereditaryStratigraphicSurface(
            dsurf.Surface(algo, S),
            predeposit_strata=0,
            stratum_differentia_bit_width=differentia_bitwidth,
        )
        for _ in range(3)
    ]
    # Deposit exactly S strata so dstream_T == S (zero generations elapsed)
    for surf in surfaces:
        surf.DepositStrata(S)

    df = pl.DataFrame(
        [
            {
                "data_hex": hstrat.surf_to_hex(
                    surf, dstream_T_bitwidth=dstream_T_bitwidth
                ),
                "dstream_algo": f"dstream.{algo.__name__.split('.')[-1]}",
                "dstream_storage_bitoffset": dstream_T_bitwidth,
                "dstream_storage_bitwidth": surf.S * differentia_bitwidth,
                "dstream_T_bitoffset": 0,
                "dstream_T_bitwidth": dstream_T_bitwidth,
                "dstream_S": surf.S,
            }
            for surf in surfaces
        ]
    )
    raw = surface_unpack_reconstruct(df)
    res = surface_postprocess_trie(
        raw,
        trie_postprocessor=AssignOriginTimeNodeRankTriePostprocessor(
            t0="dstream_S",
        ),
    )
    assert len(res) > 0
    assert "origin_time" in res.columns
    assert pfl.alifestd_validate(
        pfl.alifestd_try_add_ancestor_list_col(res.to_pandas()),
    )


@pytest.mark.parametrize("num_subtrees", [1, 50, 5000])
def test_prefix_roots_preserves_topological_order(num_subtrees: int):
    S = 4
    rows = [(0, 0, 0, None), (1, 0, 1, None), (2, 1, 2, None)]  # trunk
    next_id, next_data_id = 3, 0
    for i in range(num_subtrees):
        subtree_root = next_id
        rows.append((subtree_root, 2, S + 5 + i % 7, None))
        next_id += 1
        for __ in range(2):
            rows.append((next_id, subtree_root, S + 40, next_data_id))
            next_id += 1
            next_data_id += 1

    ids, ancestor_ids, ranks, data_ids = zip(*rows)
    raw = pl.DataFrame(
        {
            "id": ids,
            "ancestor_id": ancestor_ids,
            "dstream_rank": ranks,
            "dstream_data_id": data_ids,
            "hstrat_differentia_bitwidth": [8] * len(ids),
            "dstream_S": [S] * len(ids),
        },
        schema={
            "id": pl.UInt64,
            "ancestor_id": pl.UInt64,
            "dstream_rank": pl.UInt64,
            "dstream_data_id": pl.UInt64,
            "hstrat_differentia_bitwidth": pl.UInt32,
            "dstream_S": pl.UInt32,
        },
    )

    res = surface_postprocess_trie(
        raw,
        trie_postprocessor=AssignOriginTimeNodeRankTriePostprocessor(),
    )

    # each subtree gains one prefixed root; trunk is deleted
    assert len(res) == 4 * num_subtrees
    assert pfl.alifestd_is_topologically_sorted_polars(res)
    assert pfl.alifestd_has_contiguous_ids_polars(res)
    assert res["dstream_data_id"].drop_nulls().sort().to_list() == [
        *range(2 * num_subtrees)
    ]
