from iterpop import iterpop as ip
import numpy as np
import pandas as pd
import pandera as pa
import pytest

from hstrat import hstrat
from hstrat._auxiliary_lib import raises


@pytest.mark.parametrize(
    "specimen",
    [
        pd.Series(data=[101, 1], index=[0, 3], dtype="uint8"),
        pd.Series(data=[101, 1], index=[0, 3], dtype="uint16"),
        pd.Series(data=[101, 1], index=[0, 3], dtype="uint32"),
        pd.Series(data=[101, 1], index=[0, 3], dtype="uint64"),
    ],
)
def test_hereditary_stratigraphic_specimen_true(specimen):
    assert not all(
        raises(
            lambda: pa.SeriesSchema(ip.popsingleton(series.__args__)).validate(
                specimen
            ),
            pa.errors.SchemaError,
        )
        for series in hstrat.HereditaryStratigraphicSpecimen.__args__
    )


@pytest.mark.parametrize(
    "notspecimen",
    [
        pd.Series(data=[101, 1], index=[0, 3], dtype="int8"),
        pd.Series(data=[101, np.nan], index=[0, 3], dtype="UInt16"),
        pd.Series(data=[101, 1], index=[0, 3], dtype=float),
    ],
)
def test_hereditary_stratigraphic_specimen_false(notspecimen):

    assert all(
        raises(
            lambda: pa.SeriesSchema(ip.popsingleton(series.__args__)).validate(
                notspecimen
            ),
            pa.errors.SchemaError,
        )
        for series in hstrat.HereditaryStratigraphicSpecimen.__args__
    )
