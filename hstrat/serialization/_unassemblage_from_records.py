import typing

from ..frozen_instrumentation import HereditaryStratigraphicSpecimen
from ._impl import col_records_from_pop_records
from ._specimen_from_records import specimen_from_records


def unassemblage_from_records(
    records: typing.Dict,
    progress_wrap: typing.Callable = lambda x: x,
    mutate: bool = False,
) -> typing.List[HereditaryStratigraphicSpecimen]:
    """Deserialize a population of `HereditaryStratigraphicColumn`s into a
    list of `HereditaryStratigraphiSpecimen` from a dict composed of builtin
    types.

    Parameters
    ----------
    records : dict
        Data to deserialize.
    progress_wrap : Callable, default identity function
        Wrapper applied around generation iterator and row generator for final
        phylogeny compilation process.

        Pass tqdm or equivalent to display progress bars.
    mutate : bool, default False
        Are side effects on the input argument `records` allowed?

    See Also
    --------
    HereditaryStratigraphicSpecimen
        Postprocessing representation of the differentia retained by an extant
        HereditaryStratigraphicColumn, indexed by deposition rank.
    HereditaryStratigraphicAssemblage
        A collection of HereditaryStratigraphicSpecimens, padded to include
        entries for all ranks retained by any specimen within the assemblage.
    """

    col_records = col_records_from_pop_records(records, mutate=mutate)

    return [
        specimen_from_records(col_record)
        for col_record in progress_wrap(col_records)
    ]
