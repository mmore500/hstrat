import typing

import pandas as pd

from ..genome_instrumentation import HereditaryStratigraphicColumn
from ._col_to_dataframe import col_to_dataframe


def pop_to_dataframe(
    columns: typing.Iterable[HereditaryStratigraphicColumn],
    progress_wrap: typing.Callable = lambda x: x,
) -> pd.DataFrame:
    """Create a pandas `DataFrame` summarizing several columns, with retained
    strata as rows.

    Parameters
    ----------
    columns : iterable of HereditaryStratigraphicColumn
        Data to serialize.
    progress_wrap : Callable, default identity function
        Wrapper applied around generation iterator and row generator for final
        phylogeny compilation process.

        Pass tqdm or equivalent to display progress bars.
    """
    columns = [*map(col_to_dataframe, progress_wrap(columns))]
    return (
        pd.concat(
            columns,
            # create multiindex, with outer as column id
            keys=range(len(columns)),
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
