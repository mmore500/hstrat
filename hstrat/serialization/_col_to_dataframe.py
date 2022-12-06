import pandas as pd

from ..genome_instrumentation import HereditaryStratigraphicColumn


def col_to_dataframe(column: HereditaryStratigraphicColumn) -> pd.DataFrame:
    records = [
        {
            "index": index,
            "rank": column.GetRankAtColumnIndex(index),
            "differentia": stratum.GetDifferentia(),
        }
        for index, stratum in enumerate(column.IterRetainedStrata())
    ]
    return pd.DataFrame.from_records(records).astype(int)
