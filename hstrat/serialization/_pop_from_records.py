import typing

from ..genome_instrumentation import HereditaryStratigraphicColumn
from ._col_from_records import col_from_records
from ._impl import col_records_from_pop_records


def pop_from_records(
    records: typing.Dict,
    progress_wrap: typing.Callable = lambda x: x,
    mutate: bool = False,
) -> typing.List[HereditaryStratigraphicColumn]:
    """Deserialize a sequence of `HereditaryStratigraphicColumn`s from a dict
    composed of builtin types.

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

    Returns
    -------
    population : List[HereditaryStratigraphicColumn]
        Deserialized population of HereditaryStratigraphicColumns.
    """

    col_records = col_records_from_pop_records(records, mutate=mutate)

    return [
        col_from_records(col_record)
        for col_record in progress_wrap(col_records)
    ]
