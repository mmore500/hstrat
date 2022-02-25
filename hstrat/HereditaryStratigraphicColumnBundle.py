from copy import copy
import math
import operator
import typing

from .HereditaryStratigraphicColumn import HereditaryStratigraphicColumn


class HereditaryStratigraphicColumnBundle:
    """Packages multiple HereditaryStratigraphicColumn instances together in
    order to conveniently advance them in sync along a line of descent with a
    similar interface to an individual HereditaryStratigraphicColumn.
    """

    _columns: typing.Dict[str, HereditaryStratigraphicColumn]

    def __init__(
        self: 'HereditaryStratigraphicColumnBundle',
        columns: typing.Dict[str, HereditaryStratigraphicColumn],
    ):
        """Construct bundle.

        Parameters
        ----------
        columns : dict
            HereditaryStratigraphicColumn objects to bundle together, each
            associated with a unique names as its key.
        """
        assert len(columns), \
            "Must provide at least one column to " \
            "HereditaryStratigraphicColumnBundle."
        assert len({c.GetNumStrataDeposited() for c in columns.values()}) == 1,\
            "All columns provided ot HereditaryStratigraphicColumnBundle " \
            "must have same number strata deposited. "
        self._columns = columns

    def __getitem__(
        self: 'HereditaryStratigraphicColumnBundle' ,
        key: str,
    ) -> HereditaryStratigraphicColumn:
        """Brackets operator; access constituent column by name."""

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
        """Elapse a generation on all constituent columns.

        Parameters
        ----------
        annotation: any, optional
            Optional object to store as an annotation. Allows arbitrary user-
            provided to be associated with this stratum's generation in its
            line of descent.
        """
        for column in self._columns.values():
            column.DepositStratum(
                annotation=annotation,
            )

    def GetNumStrataDeposited(
        self: 'HereditaryStratigraphicColumnBundle',
    ) -> int:
        """How many strata have been deposited on constituent columns?

        Should be identical across constituent columns."""
        return next(iter(self._columns.values())).GetNumStrataDeposited()

    def Clone(
            self: 'HereditaryStratigraphicColumnBundle',
    ) -> 'HereditaryStratigraphicColumnBundle':
        """Create a copy of the bundle with identical data that may be freely
        altered without affecting data within this bundle."""

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
        """Return a cloned bundle that has had an additional stratum deposited.

        Does not alter self."""

        res = self.Clone()
        res.DepositStratum(annotation=stratum_annotation)
        return res
