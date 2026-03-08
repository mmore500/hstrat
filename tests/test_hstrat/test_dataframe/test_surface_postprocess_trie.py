import os
import types

from downstream import dstream, dsurf
from phyloframe import legacy as pfl
import polars as pl

from hstrat import hstrat
from hstrat.dataframe import (
    surface_postprocess_trie,
    surface_unpack_reconstruct,
)
from hstrat.phylogenetic_inference.tree.trie_postprocess import (
    AssignOriginTimeNodeRankTriePostprocessor,
)

assets_path = os.path.join(os.path.dirname(__file__), "assets")


def _make_packed_df(
    surfaces,
    algo: types.ModuleType,
    stratum_differentia_bit_width: int,
    dstream_T_bitwidth: int = 8,
) -> pl.DataFrame:
    """Build a Polars DataFrame with dstream metadata from surfaces."""
    rows = []
    for surf in surfaces:
        hex_string = hstrat.surf_to_hex(
            surf,
            dstream_T_bitwidth=dstream_T_bitwidth,
        )
        rows.append(
            {
                "data_hex": hex_string,
                "dstream_algo": f"dstream.{algo.__name__.split('.')[-1]}",
                "dstream_storage_bitoffset": dstream_T_bitwidth,
                "dstream_storage_bitwidth": surf.S
                * stratum_differentia_bit_width,
                "dstream_T_bitoffset": 0,
                "dstream_T_bitwidth": dstream_T_bitwidth,
                "dstream_S": surf.S,
            },
        )
    return pl.DataFrame(rows)


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


def test_zero_generations_elapsed():
    """Postprocessing should handle surfaces with zero generations elapsed.

    When dstream_T == dstream_S, no generations have elapsed beyond the
    founding ancestor's initial surface fill. This should not cause errors
    or produce an empty result.
    """
    S = 8
    differentia_bitwidth = 8
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

    df = _make_packed_df(surfaces, algo, differentia_bitwidth)
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
