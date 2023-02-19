from copy import copy
import operator
import typing

from ._HereditaryStratigraphicColumn import HereditaryStratigraphicColumn


class HereditaryStratigraphicColumnBundle:
    """Packages multiple HereditaryStratigraphicColumn instances together.

    Allows packaged columsn to conveniently advance in sync along a line of
    descent with a similar interface to an individual
    HereditaryStratigraphicColumn.
    """

    __slots__ = ("_columns",)

    _columns: typing.Dict[str, HereditaryStratigraphicColumn]

    def __init__(
        self: "HereditaryStratigraphicColumnBundle",
        columns: typing.Dict[str, HereditaryStratigraphicColumn],
    ):
        """Construct bundle.

        Parameters
        ----------
        columns : dict
            HereditaryStratigraphicColumn objects to bundle together, each
            associated with a unique names as its key.
        """
        assert len(columns), (
            "Must provide at least one column to "
            "HereditaryStratigraphicColumnBundle."
        )
        assert (
            len({c.GetNumStrataDeposited() for c in columns.values()}) == 1
        ), (
            "All columns provided ot HereditaryStratigraphicColumnBundle "
            "must have same number strata deposited. "
        )
        self._columns = columns

    def __iter__(
        self: "HereditaryStratigraphicColumnBundle",
    ) -> typing.Iterator[str]:
        """Iterate over held columns."""
        yield from self._columns

    def __getitem__(
        self: "HereditaryStratigraphicColumnBundle",
        key: str,
    ) -> HereditaryStratigraphicColumn:
        """Brackets operator; access constituent column by name."""
        return self._columns[key]

    def __eq__(
        self: "HereditaryStratigraphicColumnBundle",
        other: "HereditaryStratigraphicColumnBundle",
    ) -> bool:
        """Compare for value-wise equality."""
        # adapted from https://stackoverflow.com/a/4522896
        return (
            isinstance(
                other,
                self.__class__,
            )
            and self.__slots__ == other.__slots__
            and all(
                getter(self) == getter(other)
                for getter in [
                    operator.attrgetter(attr) for attr in self.__slots__
                ]
            )
        )

    def DepositStratum(
        self: "HereditaryStratigraphicColumnBundle",
        annotation: typing.Optional[typing.Any] = None,
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
        self: "HereditaryStratigraphicColumnBundle",
    ) -> int:
        """How many strata have been deposited on constituent columns?

        Should be identical across constituent columns.
        """
        return next(iter(self._columns.values())).GetNumStrataDeposited()

    def Clone(
        self: "HereditaryStratigraphicColumnBundle",
    ) -> "HereditaryStratigraphicColumnBundle":
        """Create a copy of the bundle.

        Copy contains identical data but may be freely altered without
        affecting data within this bundle.
        """
        # shallow copy
        result = copy(self)
        # do semi-shallow clone on select elements
        # see https://stackoverflow.com/a/5861653 for performance consierations
        result._columns = {k: v.Clone() for k, v in self._columns.items()}
        return result

    def CloneDescendant(
        self: "HereditaryStratigraphicColumnBundle",
        stratum_annotation: typing.Optional[typing.Any] = None,
    ) -> "HereditaryStratigraphicColumnBundle":
        """Return a cloned bundle that has had an additional stratum deposited.

        Does not alter self.

        Parameters
        ----------
        stratum_annotation: any, optional
            Optional object to store as an annotation. Allows arbitrary user-
            provided to be associated with this stratum deposition in the
            line of descent.
        """
        res = self.Clone()
        res.DepositStratum(annotation=stratum_annotation)
        return res

    def __getattr__(
        self: "HereditaryStratigraphicColumnBundle",
        attr: str,
    ) -> typing.Union[typing.Callable, typing.Dict]:
        """Forward all unknown method calls and property accesses.

        Forward to underlying ereditaryStratigraphicColumns, returning a dict
        of results for each column key stored.

        Note that __getattr__ is only called after other attribute lookup (i.e.,
        explicitly provided methods and properties) has failed.
        """
        # Adapted from
        # https://rosettacode.org/wiki/Respond_to_an_unknown_method_call#Python

        # raise AttributeError for dunder methods so that callers expecting
        # them unimplemented can catch and run their fallbacks
        if "__" in attr:
            raise AttributeError

        def arg_debundler(args, column_name) -> typing.List:
            """If any args are column bundles, extract the focal column."""
            return [
                arg
                if not isinstance(arg, self.__class__)
                else arg[column_name]
                for arg in args
            ]

        def kwarg_debundler(kwargs, column_name) -> typing.Dict:
            """If any kwarg vals are column bundles, extract focal column."""
            return {
                k: v if not isinstance(v, self.__class__) else v[column_name]
                for k, v in kwargs.items()
            }

        if any(
            callable(getattr(column, attr))
            for column in self._columns.values()
        ):
            # method forwarding
            assert all(
                callable(getattr(column, attr))
                for column in self._columns.values()
            )

            def forwarded(*args, **kwargs) -> typing.Dict:
                """Apply method to each column independently.

                Extracts the corresponding column from any column bundles passed as arguments. Returns a dict mapping each column name to its result.
                """
                return {
                    column_name: getattr(column, attr)(
                        *arg_debundler(args, column_name),
                        **kwarg_debundler(kwargs, column_name),
                    )
                    for column_name, column in self._columns.items()
                }

            return forwarded

        else:
            # property forwarding
            return {
                column_name: getattr(column, attr)
                for column_name, column in self._columns.items()
            }
