import math

from ._UniformPrior import UniformPrior


class ExponentialPrior:
    """Enacts a prior expectation that the generation of the most recent common
    ancestor (MRCA) between extant hereditary stratigraphic columns becomes
    exponentialy less likely with increasing antiquity.

    This prior provides a continuous approximation of the geometric
    distribution of time to MRCA expected under the Wright-Fisher model [1].

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
        An exact, discrete analog of this prior.
    """

    _growth_factor: float

    def __init__(self: "ExponentialPrior", growth_factor: float):
        self._growth_factor = growth_factor

    def CalcIntervalProbabilityProxy(
        self: "ExponentialPrior", begin_rank: int, end_rank: int
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

        if f == 1.0:
            return UniformPrior().CalcIntervalProbabilityProxy(
                begin_rank, end_rank
            )

        # correction to center interval mean on begin_rank
        # for interval size 1, has numerical precision issues and
        # doesn't appear to correct discretization bias
        # correction = (-f + np.log(f) + 1) / (np.log(f) - f * np.log(f))
        # begin_rank = begin_rank - 1 + correction
        # end_rank = end_rank - 1 + correction

        # simplification: remove 1/log(f) multiplicative constant
        # of integral... constant scaling won't affect weighting result
        return f**end_rank - f**begin_rank

    def CalcIntervalConditionedMean(
        self: "ExponentialPrior", begin_rank: int, end_rank: int
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
        f = self._growth_factor

        if f == 1.0:
            return UniformPrior().CalcIntervalConditionedMean(
                begin_rank, end_rank
            )

        if begin_rank == end_rank - 1:
            return begin_rank
        #
        # \int{f^x \, dx}_a^b = (f^b - f^a) / \log(f)
        #
        # so p(x) = \log(f) * f^x / (f^b - f^a)
        #
        # \int{x f^x \, dx}_a^c
        #    = ( f^a - a f^a \log(f) - f^c + c f^c \log(f) )
        #      / \log^2(f)
        #
        # \int{x p(x) \, dx}_a^b
        #    = (a f**a - b f**b ) / (f**a - f**b)
        #      - (f^b - f^a) / ( (f**a - f**b) \log(f) )
        #    = (a f**a - b f**b ) / (f**a - f**b)
        #      + 1 / \log(f) )
        #

        a = begin_rank
        b = end_rank - 1

        return (a * f**a - b * f**b) / (f**a - f**b) - 1 / math.log(f)
