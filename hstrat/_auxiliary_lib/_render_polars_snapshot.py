import typing

import polars as pl


def render_polars_snapshot(
    df: pl.DataFrame,
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
    with pl.Config() as cfg:
        cfg.set_tbl_cols(-1)
        head = repr(df.lazy().head().collect())
        message = " ".join(
            [
                df_name,
                "df:",
                str(df.lazy().select(pl.len()).collect().item()),
                "rows\n",
                head,
            ]
        )
        return display(message)
