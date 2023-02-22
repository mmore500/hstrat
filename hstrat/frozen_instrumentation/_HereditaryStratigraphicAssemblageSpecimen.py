import typing

import pandera as pa

HereditaryStratigraphicAssemblageSpecimen = typing.Union[
    pa.typing.Series[pa.typing.UINT8()],
    pa.typing.Series[pa.typing.UINT16()],
    pa.typing.Series[pa.typing.UINT32()],
    pa.typing.Series[pa.typing.UINT64()],
]
"""Type alias for a postprocessing representation of the differentia retained
by an extant HereditaryStratigraphicColumn, indexed by deposition rank.

Differentia are stored using a nullable integer representation, which allows
for inclusion of entries for all ranks retained by any specimen within the
assemblage, even if that particualr rank is not retained by this specimen. This
allows for more efficient comparisons between specimens, due to direct
alignment.

See Also
--------
HereditaryStratigraphicSpecimen
    Specimen representation that can contain only ranks retained by that
    specimen.
HereditaryStratigraphicAssemblage
    Gathers a collection of `HereditaryStratigraphicSpecimen`s and facilitates
    creation of corresponding aligned
    `HereditaryStratigraphicAssemblageSpecimen`s.
"""
