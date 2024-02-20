import numpy as np

from ._detail import PriorBase


class GeometricPrior(PriorBase):
    """Enacts a prior expectation that the generation of the most recent common
    ancestor (MRCA) between extant hereditary stratigraphic columns becomes
    exponentialy less likely with increasing antiquity.

    This prior calculates the exact, discrete geometric distribution of time to
    MRCA expected under the Wright-Fisher model [1].

    .. [1] Alison Etheridge (2006). Course 11 - Evolution in Fluctuating
    Populations. In Mathematical Statistical Physics (pp. 489-545). Elsevier.
    https://doi.org/10.1016/S0924-8099(06)80048-X

    Notes
    -----
    A static factory function to init an instance with a growth factor
    calculated from contextual information like population size and the number
    of generations elapsed since genesis should be made available in the
    future.

    See Also
    --------
    GeometricPrior
        A continuous approximation of this prior.
    """

    _growth_factor: float

    def __init__(self: "GeometricPrior", growth_factor: float):
        self._growth_factor = growth_factor

    def CalcIntervalProbabilityProxy(
        self: "GeometricPrior", begin_rank: int, end_rank: int
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
        f = self._growth_factor
        return np.logspace(
            begin_rank,
            end_rank,
            base=f,
            endpoint=False,
            num=end_rank - begin_rank,
        ).sum()

    def CalcIntervalConditionedMean(
        self: "GeometricPrior", begin_rank: int, end_rank: int
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
        f = self._growth_factor
        return np.average(
            np.arange(begin_rank, end_rank),
            weights=np.logspace(
                begin_rank,
                end_rank,
                base=f,
                endpoint=False,
                num=end_rank - begin_rank,
            ),
        )

    def SampleIntervalConditionedValue(
        self: "GeometricPrior", begin_rank: int, end_rank: int
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
        raise NotImplementedError()
