import numpy as np
import pandas as pd

from ..frozen_instrumentation import HereditaryStratigraphicSpecimen
from ..genome_instrumentation import HereditaryStratigraphicColumn


def col_to_specimen(
    column: HereditaryStratigraphicColumn,
) -> HereditaryStratigraphicSpecimen:
    """Create a postprocessing representation of the differentia retained
    by an extant HereditaryStratigraphicColumn, indexed by deposition rank."""
    differentia = np.fromiter(
        column.IterRetainedDifferentia(),
        dtype=np.min_scalar_type(
            2 ** column.GetStratumDifferentiaBitWidth() - 1
        ),
    )
    ranks = np.fromiter(
        column.IterRetainedRanks(),
        dtype=np.min_scalar_type(column.GetNumStrataDeposited() - 1),
    )

    return pd.Series(data=differentia, index=ranks)
