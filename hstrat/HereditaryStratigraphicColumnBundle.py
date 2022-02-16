from copy import deepcopy
import math
import operator
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

    def __getitem__(
        self: 'HereditaryStratigraphicColumnBundle' ,
        key: str,
    ) -> HereditaryStratigraphicColumn:
        return self._columns[key]

    def DepositStratum(
        self: 'HereditaryStratigraphicColumnBundle',
        annotation: typing.Optional[typing.Any]=None,
    ) -> None:
        for column in self._columns.values():
            column.DepositStratum(
                annotation=annotation,
            )

    def GetNumStrataDeposited(
        self: 'HereditaryStratigraphicColumnBundle',
    ) -> int:
        return next(iter(self._columns.values())).GetNumStrataDeposited()

    def MakeDescendantColumn(
        self: 'HereditaryStratigraphicColumnBundle',
        stratum_annotation: typing.Optional[typing.Any]=None,
    ) -> 'HereditaryStratigraphicColumnBundle':
        res = deepcopy(self)
        res.DepositStratum(annotation=stratum_annotation)
        return res
