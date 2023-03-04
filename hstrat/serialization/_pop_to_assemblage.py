import typing

from ..frozen_instrumentation import HereditaryStratigraphicAssemblage
from ..genome_instrumentation import HereditaryStratigraphicColumn
from ._col_to_specimen import col_to_specimen


def pop_to_assemblage(
    columns: typing.Iterable[HereditaryStratigraphicColumn],
    progress_wrap: typing.Callable = lambda x: x,
) -> HereditaryStratigraphicAssemblage:
    """Create a postprocessing representation of the differentia retained
    by a collection of HereditaryStratigraphicColumns.

    Parameters
    ----------
    columns : iterable of HereditaryStratigraphicColumn
        Data to serialize.
    progress_wrap : Callable, default identity function
        Wrapper applied around generation iterator and row generator for final
        phylogeny compilation process.

        Pass tqdm or equivalent to display progress bars.
    """
    return HereditaryStratigraphicAssemblage(
        map(col_to_specimen, progress_wrap(columns))
    )
