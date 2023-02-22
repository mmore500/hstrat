import typing

import numpy as np
import pandera as pa

HereditaryStratigraphicSpecimen = typing.Union[
    pa.typing.Series[pa.typing.UInt8()],
    pa.typing.Series[pa.typing.UInt16()],
    pa.typing.Series[pa.typing.UInt32()],
    pa.typing.Series[pa.typing.UInt64()],
]
"""Type alias for a postprocessing representation of the differentia retained
by an extant HereditaryStratigraphicColumn, indexed by deposition rank.

See Also
--------
HereditaryStratigraphicAssemblageSpecimen
    Specimen representation that allows for easier alignment among members of
    a population without perfectly homogeneous retained ranks.
specimen_from_records
    Deserialize a `HereditaryStratigraphicSpecimen` from a dict composed of
    builtin data types.
col_to_specimen
    Create a `HereditaryStratigraphicSpecimen` from a
    `HereditaryStratigraphicColumn`.
"""
