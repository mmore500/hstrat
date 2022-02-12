import operator
import math
import typing

from .HereditaryStratigraphicColumn import HereditaryStratigraphicColumn


class HereditaryStratigraphicColumnBundle:

    _columns: typing.Dict[str, HereditaryStratigraphicColumn]

    def __init__(
        self: 'HereditaryStratigraphicColumnBundle',
        columns: typing.Dict[str, HereditaryStratigraphicColumn],
    ):
        assert len(columns)
        self._columns = columns
        self.DepositStratum()

    def __getitem__(
        self: 'HereditaryStratigraphicColumnBundle' ,
        key: str,
    ) -> HereditaryStratigraphicColumn:
        return self._columns[key]

    def DepositStratum(
        self: 'HereditaryStratigraphicColumnBundle',
    ) -> None:
        for column in self._columns.values():
            column.DepositStratum()

    def GetNumStrataDeposited(
        self: 'HereditaryStratigraphicColumnBundle',
    ) -> int:
        return next(iter(self._columns.values())).GetNumStrataDeposited()
