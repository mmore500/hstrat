import numbers

from ..._auxiliary_lib import cmp_approx


class BubbleWrappedPrior:
    """Asserts that wrapped prior receives valid inputs and produces valid
    output."""

    _prior: object

    def __init__(self: "BubbleWrappedPrior", wrapee: object):
        self._prior = wrapee

    def CalcIntervalProbabilityProxy(
        self: "BubbleWrappedPrior", begin_rank: int, end_rank: int
    ) -> float:
        """Characterize the prior probability of the MRCA generation falling
        within an interval range.

        Parameters
        ----------
        begin_rank : int
            The starting rank of the interval, inclusive.
        end_rank : int
            The ending rank of the interval, exclusive.

        Returns
        -------
        float
            The proxy statistic, proportional to the true estimated interval
            probability of the MRCA value by a fixed (but unspecified) constant
            proportion.
        """
        assert isinstance(begin_rank, numbers.Integral)
        assert isinstance(end_rank, numbers.Integral)
        assert 0 <= begin_rank < end_rank
        res = self._prior.CalcIntervalProbabilityProxy(begin_rank, end_rank)
        return res

    def CalcIntervalConditionedMean(
        self: "BubbleWrappedPrior", begin_rank: int, end_rank: int
    ) -> float:
        """Calcualate the centriod of prior probability mass within an interval
        of possible MRCA generations.

        Parameters
        ----------
        begin_rank : int
            The starting rank of the interval, inclusive.
        end_rank : int
            The ending rank of the interval, exclusive.

        Returns
        -------
        float
            The prior expected generation of MRCA conditioned on the assumption
            that the MRCA falls within the given interval.
        """
        assert isinstance(begin_rank, numbers.Integral)
        assert isinstance(end_rank, numbers.Integral)
        assert 0 <= begin_rank < end_rank
        res = self._prior.CalcIntervalConditionedMean(begin_rank, end_rank)
        assert cmp_approx(begin_rank, res) <= 0
        assert res < end_rank
        return res
