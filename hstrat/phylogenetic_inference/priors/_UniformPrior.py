import numpy as np


class UniformPrior:
    """Enacts a prior expectation that the generation of the most recent common
    ancestor (MRCA) is equally likely to occur at any generation since genesis.

    See Also
    --------
    GeometricPrior
        An exact, discrete analog of this prior.
    """

    def CalcIntervalProbabilityProxy(
        self: "UniformPrior", begin_rank: int, end_rank: int
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
        return float(end_rank - begin_rank)

    def CalcIntervalConditionedMean(
        self: "UniformPrior", begin_rank: int, end_rank: int
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
        return np.mean((begin_rank, end_rank - 1))
