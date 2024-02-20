import numpy as np

from ._detail import PriorBase


class ArbitraryPrior(PriorBase):
    """Enacts a prior probability density distribution on the generation of the
    most recent common ancestor (MRCA) between extant hereditary stratigraphic
    columns that is arbitrary, but computationally efficient.

    The prior expectation for MRCA generation is taken as equal probability
    within each interval between ranks with common strata retained by both
    extant columns up through the first retained disparity between the columns.

    Prior probability density is assumed uniformly distributed within each
    interval between coincident retained ranks. So, conditioning on the
    assumption that the true generation of the MRCA occurs within a particular
    interval, the prior expected value for the MRCA generation will be the
    midpoint of the interval.

    This prior is simple to compute, but may not meaningfully reflect the
    a reasonable pre-expectation for the MRCA generation. Importantly, the
    enacted prior expectation will depend directly on the instrumentation used
    (i.e., the distribution of coincident retained strata induced by the chosen
    stratum retention policy). For example, a wide interval between coincident
    retained ranks and a short interval between coincident retained ranks will
    be assigned equal prior probability, resulting in greater per-generation
    prior probability within the small window than within a wide window.

    This prior policy guarantees the maximum likelihood estimate to fall
    between the last retained commonality and the first retained disparity of
    two extant columns. Because each interval between coincident retained ranks
    has equal prior probability, the likelihood of the true MRCA falling within
    preceding intervals strictly decreases with qualification by spurious
    differentia collisions (i.e., common retained strata). This property makes
    maximum likelihood estimation under this prior especially efficient.
    """

    def CalcIntervalProbabilityProxy(
        self: "ArbitraryPrior", begin_rank: int, end_rank: int
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
        return 1.0

    def CalcIntervalConditionedMean(
        self: "ArbitraryPrior", begin_rank: int, end_rank: int
    ) -> float:
        """Calculate the centriod of prior probability mass within an interval
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
        return np.mean((begin_rank, end_rank - 1.0))

    def SampleIntervalConditionedValue(
        self: "ArbitraryPrior", begin_rank: int, end_rank: int
    ) -> int:
        """Sample a generation of the MRCA conditioned on the assumption that
        the MRCA falls within the given interval.

        Parameters
        ----------
        begin_rank : int
            The starting rank of the interval, inclusive.
        end_rank : int
            The ending rank of the interval, exclusive.

        Returns
        -------
        int
            A sampled generation of the MRCA, conditioned on the assumption that
            the MRCA falls within the given interval.
        """
        return np.random.uniform(begin_rank, end_rank - 1.0)
