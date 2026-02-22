import typing

from prettytable import ALL as prettytable_ALL
from prettytable import PrettyTable

from ...frozen_instrumentation import HereditaryStratigraphicAssemblage


def assemblage_to_ascii(
    assemblage: HereditaryStratigraphicAssemblage,
    key: bool = True,
    time_bookends: bool = True,
) -> str:
    """Create an ASCII table representation of
    HereditaryStratigraphicAssemblage state.

    The table is oriented vertically, with the 0th column being rank and
    subsequent columns representing individual specimens in the assemblage.

    Parameters
    ----------
    assemblage : HereditaryStratigraphicAssemblage
        The HereditaryStratigraphicAssemblage object to be converted.
    key : bool, default True
        Append a legend to the output?
    time_bookends : bool, default True
        Prepend and append "MOST ANCIENT" and "MOST RECENT" to the table?

    Returns
    -------
    str
        The ASCII representation of the HereditaryStratigraphicAssemblage
        object in tabular format.
    """
    specimens = list(assemblage.BuildSpecimens())
    if not specimens:
        return ""

    df = assemblage._assemblage_df

    field_names = ["rank"] + [f"specimen {i}" for i in range(len(specimens))]

    table = PrettyTable()
    table.field_names = field_names

    for rank in df.index:
        row = [str(int(rank))]
        for col_idx in range(len(specimens)):
            val = df.iloc[:, col_idx].loc[rank]
            if _is_null(val):
                row.append("".join("░" for __ in field_names[col_idx + 1]))
            else:
                row.append(f"{int(val):x}*")
        table.add_row(row)

    table.hrules = prettytable_ALL
    res = table.get_string()

    if time_bookends:
        pad = max(len(row) for row in res.split("\n")) - 2
        res = f"|{'MOST ANCIENT':^{pad}}|\n" + res
        res = "+" + "-" * pad + "+\n" + res

        res += f"\n|{'MOST RECENT':^{pad}}|"
        res += "\n+" + "-" * pad + "+"

    if key and "*" in res:
        res += "\n*: retained stratum"

    if key and "░" in res:
        res += "\n░: missing stratum"

    return res


def _is_null(val: typing.Any) -> bool:
    """Check if a value is null/NA, handling both pandas NA and numpy nan."""
    try:
        import pandas as pd

        if pd.isna(val):
            return True
    except (TypeError, ValueError):
        pass
    return False
