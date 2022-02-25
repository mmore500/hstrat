from copy import copy
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

    def __eq__(
        self: 'HereditaryStratigraphicColumnBundle',
        other: 'HereditaryStratigraphicColumnBundle',
    ) -> bool:
        """Compare for value-wise equality."""

        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        else:
            return False

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

    def Clone(
            self: 'HereditaryStratigraphicColumnBundle',
    ) -> 'HereditaryStratigraphicColumnBundle':
        # shallow copy
        result = copy(self)
        # do semi-shallow clone on select elements
        # see https://stackoverflow.com/a/5861653 for performance consierations
        result._columns = {
            k : v.Clone()
            for k, v in self._columns.items()
        }
        return result

    def CloneDescendant(
        self: 'HereditaryStratigraphicColumnBundle',
        stratum_annotation: typing.Optional[typing.Any]=None,
    ) -> 'HereditaryStratigraphicColumnBundle':
        res = self.Clone()
        res.DepositStratum(annotation=stratum_annotation)
        return res
