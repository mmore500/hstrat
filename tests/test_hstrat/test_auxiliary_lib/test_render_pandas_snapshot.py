import pandas as pd

from hstrat._auxiliary_lib import render_pandas_snapshot


def test_smoke():
    df = pd.DataFrame(
        {
            "foo": [1, 2, 3],
            "bar": [6, 7, 8],
            "ham": ["buzz", "baz", "bang"],
        }
    )
    assert "buzz" in render_pandas_snapshot(df)
    assert "bazinga" in render_pandas_snapshot(df, "bazinga")
    assert "zzub" in render_pandas_snapshot(df, display=lambda x: x[::-1])
