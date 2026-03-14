from packaging.version import parse as parse_version
import pandas as pd
import pytest

mark_skipif_pandas_post3 = pytest.mark.skipif(
    parse_version(pd.__version__) >= parse_version("3"),
    reason="alifestd functions are not compatible with pandas >= 3",
)
