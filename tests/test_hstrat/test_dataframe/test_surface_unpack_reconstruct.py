import os

import polars as pl

from hstrat.dataframe import surface_unpack_reconstruct

assets_path = os.path.join(os.path.dirname(__file__), "assets")


def test_smoke():
    df = pl.read_csv(f"{assets_path}/packed.csv")
    surface_unpack_reconstruct(df)
