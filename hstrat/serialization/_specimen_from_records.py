import typing

import numpy as np
import pandas as pd

from .._auxiliary_lib import (
    get_hstrat_version,
    log_once_in_a_row,
    numpy_fromiter_polyfill,
)
from ..frozen_instrumentation import HereditaryStratigraphicSpecimen
from ._impl import policy_from_record
from ._unpack_differentiae_str import unpack_differentiae_str


def specimen_from_records(
    records: typing.Dict,
) -> HereditaryStratigraphicSpecimen:
    """Deserialize a `HereditaryStratigraphicSpecimen` from a dict composed of
    builtin data types.

    See Also
    --------
    HereditaryStratigraphicSpecimen
        Postprocessing representation of the differentia retained
        by an extant HereditaryStratigraphicColumn, indexed by deposition rank.
    """
    if "deposition_ranks" in records:
        raise NotImplementedError

    if get_hstrat_version() != records["hstrat_version"]:
        log_once_in_a_row(
            f"""specimen_from_records version mismatch, record is version {
                records['hstrat_version']
            } and software is version {
                get_hstrat_version()
            }"""
        )

    policy = policy_from_record(records["policy"])
    differentia = numpy_fromiter_polyfill(
        unpack_differentiae_str(
            records["differentiae"],
            differentia_bit_width=records["differentia_bit_width"],
        ),
        dtype=np.min_scalar_type(2 ** records["differentia_bit_width"] - 1),
    )
    ranks = numpy_fromiter_polyfill(
        policy.IterRetainedRanks(records["num_strata_deposited"]),
        dtype=np.min_scalar_type(records["num_strata_deposited"] - 1),
    )
    return HereditaryStratigraphicSpecimen(
        pd.Series(data=differentia, index=ranks),
        records["differentia_bit_width"],
    )
