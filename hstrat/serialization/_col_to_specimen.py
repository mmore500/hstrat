import numpy as np
import pandas as pd

from .._auxiliary_lib import numpy_fromiter_polyfill
from ..frozen_instrumentation import HereditaryStratigraphicSpecimen
from ..genome_instrumentation import HereditaryStratigraphicColumn


def col_to_specimen(
    column: HereditaryStratigraphicColumn,
) -> HereditaryStratigraphicSpecimen:
    """Create a postprocessing representation of the differentia retained
    by an extant HereditaryStratigraphicColumn, indexed by deposition rank."""
    differentia = numpy_fromiter_polyfill(
        column.IterRetainedDifferentia(),
        dtype=np.min_scalar_type(
            2 ** column.GetStratumDifferentiaBitWidth() - 1
        ),
    )
    ranks = numpy_fromiter_polyfill(
        column.IterRetainedRanks(),
        dtype=np.min_scalar_type(column.GetNumStrataDeposited() - 1),
    )

    return HereditaryStratigraphicSpecimen(
        stratum_differentia_series=pd.Series(data=differentia, index=ranks),
        stratum_differentia_bit_width=column.GetStratumDifferentiaBitWidth(),
    )
