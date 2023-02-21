import copy
import typing


def col_records_from_pop_records(
    pop_records: typing.Dict,
    mutate: bool = False,
) -> typing.Iterator[typing.Dict]:
    """Generate column records from a dictionary of builtin types representing
    a serialized population of `HereditaryStratigraphicColumn`s.

    Parameters
    ----------
    pop_records : dict
        A dictionary containing the serialized population data. It must have a
        'columns' field, which is a list of dictionaries representing the
        columns.

        Other common fields will be propagated into individual column entries.
    mutate : bool, default False
        Are side effects on the input argument `pop_records` allowed?

    Yields
    ------
    dict
        Dictionariew of builtin types representing individual column records.
    """
    col_records = pop_records["columns"]

    if not mutate:
        col_records = copy.deepcopy(col_records)

    for col_record in col_records:
        for common_field in (
            "policy",
            "policy_algo",
            "policy_spec",
            "differentia_bit_width",
            "hstrat_version",
        ):
            col_record[common_field] = pop_records[common_field]
        yield col_record
