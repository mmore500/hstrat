import typing

import pandas as pd

from ._coerce_to_polars import coerce_to_polars
from ._render_polars_snapshot import render_polars_snapshot


def render_pandas_snapshot(
    df: pd.DataFrame,
    df_name: str = "",
    display: typing.Callable = lambda x: x,
) -> typing.Optional[str]:
    """Render an all-columns snapshot of the head of a Polars DataFrame.

    Parameters
    ----------
    df : pl.DataFrame
        The DataFrame to render.
    df_name : str, default ""
        The name of the DataFrame to render.
    display : Callable, optional
        The function to use to display the rendered DataFrame, e.g., print,
        logging.info, etc.

    Returns
    -------
    Optional[str]
        The rendered DataFrame, as a string, if `display` is not used.
    """
    return render_polars_snapshot(
        coerce_to_polars(df.head()), df_name=df_name, display=display
    )
