import typing

from iterpop import iterpop as ip

from ..genome_instrumentation import HereditaryStratigraphicColumn
from ._col_to_records import col_to_records


def pop_to_records(
    columns: typing.Iterable[HereditaryStratigraphicColumn],
    progress_wrap: typing.Callable = lambda x: x,
) -> typing.Dict:
    """Serialize a sequence of `HereditaryStratigraphicColumn`s to a dict
    composed of builtin types.

    Parameters
    ----------
    columns : iterable of HereditaryStratigraphicColumn
        Data to serialize.
    progress_wrap : Callable, default identity function
        Wrapper applied around generation iterator and row generator for final
        phylogeny compilation process.

        Pass tqdm or equivalent to display progress bars.
    """
    col_records = [col_to_records(column) for column in progress_wrap(columns)]

    res = {}
    for common_field in (
        "policy",
        "policy_algo",
        "policy_spec",
        "differentia_bit_width",
        "hstrat_version",
    ):
        res[common_field] = ip.pourhomogeneous(
            col_record.pop(common_field) for col_record in col_records
        )

    res["columns"] = col_records

    return res
