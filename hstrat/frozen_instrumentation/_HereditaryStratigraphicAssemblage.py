import itertools as it
import typing

from iterpop import iterpop as ip
import numpy as np
import pandas as pd

from .._auxiliary_lib import as_nullable_type
from ._HereditaryStratigraphicAssemblageSpecimen import (
    HereditaryStratigraphicAssemblageSpecimen,
)
from ._HereditaryStratigraphicSpecimen import HereditaryStratigraphicSpecimen


class HereditaryStratigraphicAssemblage:
    """A collection of HereditaryStratigraphicSpecimens, padded to include entries for all ranks retained by any specimen within the
    assemblage.

    This allows for more efficient comparisons between specimens, due to direct
    alignment.

    Parameters
    ----------
    specimens : iterable of HereditaryStratigraphicSpecimen
        The specimens that make up the assemblage.

    See Also
    --------
    HereditaryStratigraphicSpecimen
        Type alias for a postprocessing representation of the differentia
        retained by an extant HereditaryStratigraphicColumn, indexed by
        deposition rank.
    assemblage_from_records
        Deserialize a `HereditaryStratigraphicSpecimen` from a dict composed of
        builtin data types.
    pop_to_assemblage
        Create a `HereditaryStratigraphicAssemblage` from a collection of
        `HereditaryStratigraphicColumn`s.
    """

    __slots__ = ("_assemblage_df", "_stratum_differentia_bit_width")

    # rows indexed by rank
    # columns represent individuals within population, as IntegerArrays
    _assemblage_df: pd.DataFrame

    _stratum_differentia_bit_width: int

    def __init__(
        self: "HereditaryStratigraphicAssemblage",
        specimens: typing.Iterable[HereditaryStratigraphicSpecimen],
    ) -> None:
        """Construct a new HereditaryStratigraphicAssemblage instance.

        Takes a collection of HereditaryStratigraphicSpecimen instances and
        creates a new HereditaryStratigraphicAssemblage instance containing
        those specimens.
        """
        specimens1, specimens2 = it.tee(specimens)
        self._stratum_differentia_bit_width = ip.pourhomogeneous(
            specimen.GetStratumDifferentiaBitWidth() for specimen in specimens1
        )
        try:
            self._assemblage_df = pd.concat(
                (
                    as_nullable_type(specimen.GetData())
                    for specimen in specimens2
                ),
                axis="columns",
            ).sort_index()
        except ValueError:  # empty specimens
            self._assemblage_df = pd.DataFrame()

        assert not self._assemblage_df.index.isna().any()
        self._assemblage_df.index.astype(np.uint64, copy=False)

    def BuildSpecimens(
        self: "HereditaryStratigraphicAssemblage",
    ) -> typing.Iterator[HereditaryStratigraphicAssemblageSpecimen]:
        """Iterator over specimens in assemblage as potentially-padded
        HereditaryStratigraphicAssemblageSpecimen objects."""
        for _column_name, series in self._assemblage_df.items():
            yield HereditaryStratigraphicAssemblageSpecimen(
                stratum_differentia_series=series,
                stratum_differentia_bit_width=(
                    self._stratum_differentia_bit_width
                ),
            )
