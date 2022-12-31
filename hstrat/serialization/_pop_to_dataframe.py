import itertools as it
import typing

import pandas as pd

from ..genome_instrumentation import HereditaryStratigraphicColumn
from ._col_to_dataframe import col_to_dataframe


def pop_to_dataframe(
    columns: typing.Iterable[HereditaryStratigraphicColumn],
) -> pd.DataFrame:
    """Create a pandas `DataFrame` summarizing several columns, with retained
    strata as rows."""
    return (
        pd.concat(
            map(col_to_dataframe, columns),
            keys=it.count(),  # create multiindex, with outer as column id
        )
        .reset_index(  # drop original row-level index
            level=1,
            drop=True,
        )
        .rename_axis(  # set name for column id index
            ["column"],
        )
        .reset_index()
    )
