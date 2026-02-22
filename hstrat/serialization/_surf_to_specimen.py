import numpy as np
import pandas as pd

from .._auxiliary_lib import numpy_fromiter_polyfill
from ..frozen_instrumentation import HereditaryStratigraphicSpecimen
from ..genome_instrumentation import HereditaryStratigraphicSurface


def surf_to_specimen(
    surface: HereditaryStratigraphicSurface,
) -> HereditaryStratigraphicSpecimen:
    """Convert a `HereditaryStratigraphicSurface` to a
    `HereditaryStratigraphicSpecimen`.

    Unlike `col_to_specimen`, handles surfaces with negative ranks
    (pre-initialization strata) by using signed integer dtypes for the
    rank index.

    Parameters
    ----------
    surface : HereditaryStratigraphicSurface
        The surface to convert.

    Returns
    -------
    HereditaryStratigraphicSpecimen
        Specimen with differentia indexed by retained ranks.

    See Also
    --------
    col_to_specimen :
        Convert a `HereditaryStratigraphicColumn` to a specimen.
    """
    differentia = numpy_fromiter_polyfill(
        surface.IterRetainedDifferentia(),
        dtype=np.min_scalar_type(
            2 ** surface.GetStratumDifferentiaBitWidth() - 1
        ),
    )
    ranks = numpy_fromiter_polyfill(
        surface.IterRetainedRanks(),
        dtype=np.int64,
    )

    return HereditaryStratigraphicSpecimen(
        stratum_differentia_series=pd.Series(data=differentia, index=ranks),
        stratum_differentia_bit_width=surface.GetStratumDifferentiaBitWidth(),
    )
