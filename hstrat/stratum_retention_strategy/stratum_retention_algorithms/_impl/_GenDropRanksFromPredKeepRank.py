import typing

from .._detail._PolicyCouplerBase import PolicyCouplerBase


class _GenDropRanksFromPredKeepRankBase:
    """Dummy class to faciliate recognition of instantiations of the
    GenDropRanksFromPredKeepRank class across different calls to
    the GenDropRanksFromPredKeepRank factory."""


def GenDropRanksFromPredKeepRank(
    predicate: typing.Type[typing.Callable],
) -> typing.Type[typing.Callable]:
    """Factory method to generate a stratum retention condemner functor from a
    stratum retention predicate functor.

    Parameters
    ----------
    predicate : callable
        Callable specifying whether a stratum with deposition rank r should be
        retained within the hereditary stratigraphic column after n strata have
        been deposited.

    Returns
    -------
    condemner : callable
        Functor that enacts the predicate's stratum retention policy by
        specifying the set of strata ranks that should be purged from a
        hereditary stratigraphic column when the nth stratum is deposited.
    """

    class GenDropRanksFromPredKeepRank(
        _GenDropRanksFromPredKeepRankBase,
    ):
        """Functor that wraps a stratum retention predicate functor to
        operate as a stratum retention condemner."""

        _predicate: typing.Callable

        def __init__(self: "GenDropRanksFromPredKeepRank", *args, **kwargs):
            """Construct the functor.

            Arguments are forwarded to predicate constructor.
            """
            self._predicate = predicate(*args, **kwargs)

        def __call__(
            self: "GenDropRanksFromPredKeepRank",
            policy: PolicyCouplerBase,
            num_stratum_depositions_completed: int,
            retained_ranks: typing.Iterable[int],
        ) -> typing.Iterator[int]:
            def should_retain(stratum_rank: int) -> bool:
                """Should the rth stratum rank be retained?

                Asserts retention requirements are respected by predicate.
                """
                res = self._predicate(
                    policy,
                    stratum_rank=stratum_rank,
                    num_stratum_depositions_completed=num_stratum_depositions_completed,
                )
                # predicate must *always* retain the initial and latest strata
                if stratum_rank in (0, num_stratum_depositions_completed):
                    assert res
                return res

            for rank in retained_ranks:
                if not should_retain(rank):
                    yield rank
            return

        def __eq__(
            self: "GenDropRanksFromPredKeepRank",
            other: typing.Any,
        ) -> bool:
            """Compare for value-wise equality."""
            # account for possible distinct instantiations of the
            # GenDropRanksFromPredKeepRank class across calls to the
            # GenDropRanksFromPredKeepRank factory
            if issubclass(
                other.__class__,
                _GenDropRanksFromPredKeepRankBase,
            ):
                return self._predicate == other._predicate
            else:
                return False

    return GenDropRanksFromPredKeepRank
