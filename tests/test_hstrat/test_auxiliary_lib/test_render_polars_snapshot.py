import polars as pl

from hstrat._auxiliary_lib import render_polars_snapshot


def test_smoke():
    df = pl.DataFrame(
        {
            "foo": [1, 2, 3],
            "bar": [6, 7, 8],
            "ham": ["buzz", "baz", "bang"],
        }
    )
    assert "buzz" in render_polars_snapshot(df)
    assert "bazinga" in render_polars_snapshot(df, "bazinga")
    assert "zzub" in render_polars_snapshot(df, display=lambda x: x[::-1])
