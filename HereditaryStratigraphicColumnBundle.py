import operator
import math
import typing

from .HereditaryStratigraphicColumn import HereditaryStratigraphicColumn

class HereditaryStratigraphicColumnBundle:

    _columns: typing.Dict[str, HereditaryStratigraphicColumn,]

    def __init__(
        self: 'HereditaryStratigraphicColumnBundle',
        columns: typing.Dict[str, HereditaryStratigraphicColumn,],
    ):
        assert len(columns)
        self._columns = columns
        self.DepositLayer()

    def __getitem__(
        self: 'HereditaryStratigraphicColumnBundle' ,
        key: str,
    ) -> HereditaryStratigraphicColumn:
        return self._columns[key]

    def DepositLayer(
        self: 'HereditaryStratigraphicColumnBundle',
    ) -> None:
        for column in self._columns.values():
            column.DepositLayer()

    def GetNumLayersDeposited(
        self: 'HereditaryStratigraphicColumnBundle',
    ) -> int:
        return next(iter(self._columns.values())).GetNumLayersDeposited()
