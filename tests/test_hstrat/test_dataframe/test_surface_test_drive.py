import os

import polars as pl

from hstrat._auxiliary_lib import alifestd_count_leaf_nodes
from hstrat.dataframe import surface_test_drive

assets_path = os.path.join(os.path.dirname(__file__), "assets")


def test_smoke():
    df = pl.read_csv(f"{assets_path}/nk_ecoeaselection.csv")
    df = df.with_columns(foo=pl.lit("bar"))
    pop = surface_test_drive(
        df,
        dstream_algo="dstream.steady_algo",
        dstream_S=64,
        stratum_differentia_bit_width=1,
    )
    assert len(pop) == alifestd_count_leaf_nodes(df)
    assert "origin_time" in pop.columns
    assert "data_hex" in pop.columns
    assert (pop["dstream_storage_bitwidth"] == 64).all()
    assert "dstream_storage_bitoffset" in pop.columns
    assert "dstream_T_bitwidth" in pop.columns
    assert "dstream_T_bitoffset" in pop.columns
    assert "dstream_S" in pop.columns
    assert "dstream_algo" in pop.columns
    assert "foo" in pop.columns
    assert "td_source_id" in pop.columns
    assert set(zip(pop["td_source_id"], pop["origin_time"])) <= set(
        zip(df["id"], df["origin_time"]),
    )
