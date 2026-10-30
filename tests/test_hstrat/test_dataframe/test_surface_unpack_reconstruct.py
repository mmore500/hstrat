import os
import random
import re

from downstream import dstream, dsurf
from phyloframe import legacy as pfl
import polars as pl
import pytest

from hstrat import hstrat
from hstrat.dataframe import surface_unpack_reconstruct
from hstrat.dataframe.surface_unpack_reconstruct import _create_parser

assets_path = os.path.join(os.path.dirname(__file__), "assets")


@pytest.mark.parametrize("pa_source_type", ["memory_map", "OSFile"])
def test_smoke(pa_source_type: str):
    df = pl.read_csv(f"{assets_path}/packed.csv")
    res = surface_unpack_reconstruct(df, pa_source_type=pa_source_type)
    assert len(res) > len(df)
    assert pfl.alifestd_validate(
        pfl.alifestd_try_add_ancestor_list_col(res.to_pandas()),
    )
    assert pfl.alifestd_is_chronologically_ordered(
        pfl.alifestd_try_add_ancestor_list_col(
            res.with_columns(origin_time=pl.col("dstream_rank")).to_pandas(),
        ),
    )


@pytest.mark.parametrize("mp_pool_size", [1, 2])
def test_mp_pool_size(mp_pool_size: int):
    df = pl.read_csv(f"{assets_path}/packed.csv")
    res = surface_unpack_reconstruct(df, mp_pool_size=mp_pool_size)
    assert len(res) > len(df)
    assert pfl.alifestd_validate(
        pfl.alifestd_try_add_ancestor_list_col(res.to_pandas()),
    )
    assert pfl.alifestd_is_chronologically_ordered(
        pfl.alifestd_try_add_ancestor_list_col(
            res.with_columns(origin_time=pl.col("dstream_rank")).to_pandas(),
        ),
    )


def test_drop_dstream_metadata_default():
    """Default behavior (None) should drop dstream/downstream columns."""
    df = pl.read_csv(f"{assets_path}/packed.csv")
    res = surface_unpack_reconstruct(df)
    dstream_cols = [
        c
        for c in res.columns
        if re.match(r"^dstream_", c) or re.match(r"^downstream_", c)
    ]
    # only dstream_data_id, dstream_S, and dstream_rank should survive
    assert set(dstream_cols) == {
        "dstream_data_id",
        "dstream_S",
        "dstream_rank",
    }


def test_drop_dstream_metadata_true_raises():
    """Passing drop_dstream_metadata=True should raise NotImplementedError."""
    df = pl.read_csv(f"{assets_path}/packed.csv")
    with pytest.raises(NotImplementedError):
        surface_unpack_reconstruct(df, drop_dstream_metadata=True)


def test_parser_no_prefix_matching_drop():
    """Regression: --drop must not prefix-match --drop-dstream-metadata.

    The parser uses parse_known_args before joinem registers --drop.
    Without allow_abbrev=False, argparse prefix-matches --drop to
    --drop-dstream-metadata, causing conflicts when both --drop and
    --no-drop-dstream-metadata appear on the same command line.
    """
    parser = _create_parser()
    # --drop is not registered on this parser (joinem adds it later),
    # so it should pass through as an unknown arg
    args, remaining = parser.parse_known_args(
        [
            "--no-drop-dstream-metadata",
            "--drop",
            "awoo",
            "/dev/null",
        ],
    )
    assert args.drop_dstream_metadata is False
    assert "--drop" in remaining
    assert "awoo" in remaining


def test_empty():
    """Regression: empty genome set should produce an empty phylogeny without
    crashing, with the same columns and types as a non-empty result."""
    df = pl.read_csv(f"{assets_path}/packed.csv")
    full = surface_unpack_reconstruct(df)

    res = surface_unpack_reconstruct(df.head(0))
    assert len(res) == 0
    assert set(res.schema.names()) == set(full.schema.names())
    for col in full.schema.names():
        assert (
            res.schema[col] == full.schema[col]
        ), f"type mismatch for {col}: {res.schema[col]} != {full.schema[col]}"


def test_single_genome():
    """Regression: a single genome should produce a valid phylogeny."""
    df = pl.read_csv(f"{assets_path}/packed.csv").head(1)
    res = surface_unpack_reconstruct(df)
    assert len(res) >= 1
    assert pfl.alifestd_validate(
        pfl.alifestd_try_add_ancestor_list_col(res.to_pandas()),
    )
    assert pfl.alifestd_is_chronologically_ordered(
        pfl.alifestd_try_add_ancestor_list_col(
            res.with_columns(origin_time=pl.col("dstream_rank")).to_pandas(),
        ),
    )


def test_shuffle_over_same_T_seed():
    """Smoke test: shuffle_over_same_T_seed produces a valid phylogeny."""
    df = pl.read_csv(f"{assets_path}/packed.csv")
    res = surface_unpack_reconstruct(df, shuffle_over_same_T_seed=42)
    assert len(res) > len(df)
    assert pfl.alifestd_validate(
        pfl.alifestd_try_add_ancestor_list_col(res.to_pandas()),
    )
    assert pfl.alifestd_is_chronologically_ordered(
        pfl.alifestd_try_add_ancestor_list_col(
            res.with_columns(
                origin_time=pl.col("dstream_rank"),
            ).to_pandas(),
        ),
    )


def test_drop_dstream_metadata_false():
    """Passing drop_dstream_metadata=False should retain dstream columns."""
    df = pl.read_csv(f"{assets_path}/packed.csv")
    res = surface_unpack_reconstruct(df, drop_dstream_metadata=False)
    assert len(res) > len(df)
    # dstream columns from input should be forwarded
    input_dstream_cols = {
        c
        for c in df.columns
        if re.match(r"^dstream_", c) or re.match(r"^downstream_", c)
    }
    output_dstream_cols = {
        c
        for c in res.columns
        if re.match(r"^dstream_", c) or re.match(r"^downstream_", c)
    }
    # all original dstream columns should be present in output
    assert input_dstream_cols <= output_dstream_cols


def _make_evolved_population_df(
    differentia_bitwidth: int, seed: int, S: int = 16
) -> pl.DataFrame:
    rng = random.Random(seed)
    founder = hstrat.HereditaryStratigraphicSurface(
        dsurf.Surface(dstream.steady_algo, S),
        stratum_differentia_bit_width=differentia_bitwidth,
    )
    population = [founder]
    for __ in range(80):
        population = [
            rng.choice(population).CloneDescendant() for __ in range(16)
        ]
    dstream_T_bitwidth = 32
    return pl.DataFrame(
        [
            {
                "data_hex": hstrat.surf_to_hex(
                    surf, dstream_T_bitwidth=dstream_T_bitwidth
                ),
                "dstream_algo": "dstream.steady_algo",
                "dstream_storage_bitoffset": dstream_T_bitwidth,
                "dstream_storage_bitwidth": S * differentia_bitwidth,
                "dstream_T_bitoffset": 0,
                "dstream_T_bitwidth": dstream_T_bitwidth,
                "dstream_S": S,
            }
            for surf in population
        ],
    )


@pytest.mark.parametrize("differentia_bitwidth", [1, 8, 64])
@pytest.mark.parametrize("collapse_unif_freq", [1, 3, -1])
def test_collapsed_unifurcations_independent_of_collapse_freq(
    differentia_bitwidth: int, collapse_unif_freq: int
):
    # tallies accumulated across intermediate (dropped-only) collapses
    # should match a single collapse at the end of reconstruction
    df = _make_evolved_population_df(differentia_bitwidth, seed=1)
    kwargs = dict(exploded_slice_size=2, drop_dstream_metadata=False)
    expected = surface_unpack_reconstruct(df, collapse_unif_freq=0, **kwargs)
    res = surface_unpack_reconstruct(
        df, collapse_unif_freq=collapse_unif_freq, **kwargs
    )
    assert res.sort("id").equals(expected.sort("id"))
    assert res["hstrat_collapsed_unifurcations"].null_count() == 0
    assert res["hstrat_collapsed_unifurcations"].sum() > 0


@pytest.mark.parametrize("differentia_bitwidth", [1, 8, 64])
def test_collapsed_unifurcations_bounded_by_rank_gap(
    differentia_bitwidth: int,
):
    # collapsed unifurcations lie strictly between a node and its ancestor,
    # at distinct ranks
    res = surface_unpack_reconstruct(
        _make_evolved_population_df(differentia_bitwidth, seed=2),
        drop_dstream_metadata=False,
    )
    ranks = res["dstream_rank"].cast(pl.Int64).to_numpy()
    ancestor_ranks = ranks[res["ancestor_id"].to_numpy()]
    is_root = res["id"].to_numpy() == res["ancestor_id"].to_numpy()
    tallies = res["hstrat_collapsed_unifurcations"].to_numpy()
    assert (tallies[is_root] == 0).all()
    assert (tallies[~is_root] < (ranks - ancestor_ranks)[~is_root]).all()
