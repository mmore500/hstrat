import typing

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

    __slots__ = ("_assemblage_df",)

    # rows indexed by rank
    # columns represent individuals within population, as IntegerArrays
    _assemblage_df: pd.DataFrame

    def __init__(
        self: "HereditaryStratigraphicAssemblage",
        specimens: typing.Iterable[HereditaryStratigraphicSpecimen],
    ) -> None:
        """Construct a new HereditaryStratigraphicAssemblage instance.

        Takes an iterable of HereditaryStratigraphicSpecimen instances and
        creates a new HereditaryStratigraphicAssemblage instance containing
        those specimens.
        """
        try:
            self._assemblage_df = pd.concat(
                (as_nullable_type(specimen) for specimen in specimens),
                axis="columns",
            )
        except ValueError:  # empty specimens
            self._assemblage_df = pd.DataFrame()

    def IterSpecimens(
        self: "HereditaryStratigraphicAssemblage",
    ) -> typing.Iterator[HereditaryStratigraphicAssemblageSpecimen]:
        """Iterator over specimens in assemblage as potentially-padded
        HereditaryStratigraphicAssemblageSpecimen objects."""
        for _name, values in self._assemblage_df.items():
            yield values
