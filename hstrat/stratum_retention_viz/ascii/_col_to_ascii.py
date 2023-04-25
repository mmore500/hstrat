from prettytable import ALL as prettytable_ALL
from prettytable import PrettyTable

from ...genome_instrumentation import HereditaryStratigraphicColumn
from ...serialization import col_to_dataframe


def col_to_ascii(
    column: HereditaryStratigraphicColumn,
    discarded_strata: bool = True,
    key: bool = True,
    time_bookends: bool = True,
) -> str:
    df = col_to_dataframe(column)
    df.set_index("rank", inplace=True)

    table = PrettyTable()
    table.field_names = [
        "stratum rank",
        "stratum index",
        "stratum differentia",
    ]

    wrap_rank = (
        lambda rank: f"({rank})"
        if column._ShouldOmitStratumDepositionRank()
        else str(rank)
    )

    for rank in (
        range(column.GetNumStrataDeposited()) if discarded_strata else df.index
    ):
        if rank in df.index:
            row = df.loc[rank]
            table.add_row(
                [
                    wrap_rank(rank),
                    row["index"],
                    f"{int(row['differentia']):x}*",
                ]
            )
        else:
            table.add_row(
                [
                    rank,
                    "".join("░" for __ in "stratum index"),
                    "".join("░" for __ in "stratum differentia"),
                ]
            )

    table.hrules = prettytable_ALL
    res = table.get_string()

    if time_bookends:
        pad = max(len(row) for row in res.split("\n")) - 2
        res = f"|{'MOST ANCIENT':^{pad}}|\n" + res
        res = "+" + "-" * pad + "+\n" + res

        res += f"\n|{'MOST RECENT':^{pad}}|"
        res += "\n+" + "-" * pad + "+"

    if key and "*" in res:
        res += "\n*: stored in stratum (otherwise calculated)"

    if key and "░" in res:
        res += "\n░: discarded stratum"

    return res
