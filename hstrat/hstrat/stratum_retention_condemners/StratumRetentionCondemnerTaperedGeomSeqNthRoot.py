from iterpop import iterpop as ip
import opytional as opyt
import typing
import warnings

from ..HereditaryStratum import HereditaryStratum
from ..stratum_retention_predicates \
    import StratumRetentionPredicateTaperedGeomSeqNthRoot


class StratumRetentionCondemnerTaperedGeomSeqNthRoot(
    # inherit CalcNumStrataRetainedUpperBound, etc.
    StratumRetentionPredicateTaperedGeomSeqNthRoot,
):
    """TODO

    See Also
    --------
    StratumRetentionPredicateTaperedGeomSeqNthRoot:
        For definitions of methods inherited by this class that describe
        guaranteed properties of the nth root geometric sequence stratum retention
        policy.
    """

    def __init__(
        self: 'StratumRetentionCondemnerTaperedGeomSeqNthRoot',
        degree: int=100,
        interspersal: int=2,
    ):
        """Construct the functor.

        Parameters
        ----------
        degree : int, optional
            TODO.
        interspersal : int, optional
            TODO.
        """

        super(
            StratumRetentionCondemnerTaperedGeomSeqNthRoot,
            self,
        ).__init__(
            degree=degree,
            interspersal=interspersal,
        )

        self._cached_result = None

    def __call__(
        self: 'StratumRetentionCondemnerTaperedGeomSeqNthRoot',
        num_stratum_depositions_completed: int,
        retained_ranks: typing.Optional[typing.Iterable[int]]=None,
    ) -> typing.Iterator[int]:
        """Decide which strata within the stratagraphic column should be purged.

        Every time a new stratum is deposited, this method is called to
        determine which strata should be purged. All strata at ranks yielded
        from this functor are immediately purged from the column, meaning that
        for a stratum to persist it must not be yielded by this functor each
        and every time a new stratum is deposited.

        Parameters
        ----------
        num_stratum_depositions_completed : int
            The number of strata that have already been deposited, not
            including the latest stratum being deposited which prompted the
            current purge operation.
        retained_ranks : iterator over int, optional
            An iterator over ranks of strata currently retained within the
            hereditary stratigraphic column. Not used in this functor.

        Returns
        -------
        iterator over int
                The ranks of strata that should be purged from the hereditary
            stratigraphic column at this deposition step.

        See Also
        --------
        StratumRetentionPredicateTaperedGeomSeqNthRoot:
            For details on the rationale, implementation, and guarantees of the
            nth root geometric sequence stratum retention policy.
        """

        prev_retained_ranks = super(
            StratumRetentionCondemnerTaperedGeomSeqNthRoot,
            self,
        )._get_retained_ranks(
            num_stratum_depositions_completed,
        )

        cur_retained_ranks = super(
            StratumRetentionCondemnerTaperedGeomSeqNthRoot,
            self,
        )._get_retained_ranks(
            num_stratum_depositions_completed + 1,
        )

        # take set difference between prev retained ranks and cur retained ranks
        res = (prev_retained_ranks - cur_retained_ranks)

        # assertions to check validity of optimization
        # (thereby negating it, but that's ok)
        size_bound = super(
            StratumRetentionCondemnerTaperedGeomSeqNthRoot,
            self,
        ).CalcNumStrataRetainedUpperBound()
        if num_stratum_depositions_completed < size_bound:
            assert res == set()
        elif (
            self._degree
            and opyt.apply_if(
                self._cached_result,
                lambda x: x[0] == num_stratum_depositions_completed - 1,
            )
        ):

            cached_time, cached_drop = self._cached_result

            pow1_sep = super(
                StratumRetentionCondemnerTaperedGeomSeqNthRoot,
                self,
            )._calc_rank_sep(
                1,
                cached_drop,
            ) // 2
            if pow1_sep == 0:
                pow1_sep = 1

            # TODO should this be +1?
            pow1_frontstop = (
                (num_stratum_depositions_completed + 1)
                - (num_stratum_depositions_completed + 1) % pow1_sep
            )
            if pow1_frontstop - 1 < cached_drop:
                # if -2 this fails
                assert res == {
                    cached_drop + 1,
                }, (
                    res,
                    cached_drop,
                    self._degree,
                    self._interspersal,
                    pow1_sep,
                    pow1_frontstop,
                )

        if res:
            self._cached_result = (
                num_stratum_depositions_completed,
                ip.popsingleton(res),
            )
        yield from res
