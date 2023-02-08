import math
import statistics
import typing

from iterpop import iterpop as ip
import numpy as np
import opytional as opyt

from ..._auxiliary_lib import pairwise, unzip
from ...genome_instrumentation import HereditaryStratigraphicColumn
from ._impl import (
    estimate_rank_of_mrca_maximum_likelihood,
    estimate_rank_of_mrca_naive,
    estimate_rank_of_mrca_unbiased,
)


def estimate_rank_of_mrca_between(
    first: HereditaryStratigraphicColumn,
    second: HereditaryStratigraphicColumn,
    estimator: str,
    prior: str,
    prior_exponential_factor: typing.Optional[float] = None,
) -> typing.Optional[float]:
    """At what generation did the most recent common ancestor of first and
    second occur?

    Parameters
    ----------
    estimator : {"maximum_likelihood", "unbiased"}
        What estimation method should be used? Options are "maximum_likelihood"
        or "unbiased".

        The "maximum_likelihood" estimator is faster to compute than the
        "unbiased" estimator. Unbiased estimator assumes a uniform prior for
        generation of MRCA.
    prior : {"arbitrary", "uniform", "exponential"}
        Prior probability density distribution over possible generations of the
        MRCA.

        Note: accomodation of user-defined functinos for this argument can
        easily be implemented if necessary.
    prior_exponential_factor : optional float
        Specifies the exponential growth rate of the prior probability density
        over MRCA generations, only used when `prior` is set to "exponential".

        Note: a convenience function to calculate a reasonable prior
        exponential factor from population size and the number of generations that have elapsed since genesis will be made available in the future.
    Returns
    -------
    float, optional
        Estimate of MRCA rank, unless first and second definitively share no
        common ancestor in which case None will be returned.

    See Also
    --------
    calc_rank_of_mrca_bounds_between :
        Calculates confidence intervals for generation of most recent common
        ancestor between two hereditary stratigraphic columns.
    does_definitively_have_no_common_anestor :
        Does the hereditary stratigraphic record definitively prove that first
        and second could not possibly share a common ancestor?
    """

    if estimator == "maximium_likelihood" and prior == "arbitrary":
        return estimate_rank_of_mrca_naive(first, second)

    estimator = {
        "maximum_likelihood": estimate_rank_of_mrca_maximum_likelihood,
        "unbiased": estimate_rank_of_mrca_unbiased,
    }[estimator]

    assert (prior_exponential_factor is not None) == (prior == "exponential")
    f = prior_exponential_factor

    prior_interval_weight = {
        # x: interval begin generation, inclusive
        # y: interval end generation, exclusive
        "arbitrary": lambda x, y: 1,
        "uniform": lambda x, y: y - x,
        # simplification: remove 1/log(f) multiplicative constant
        # of integral... constant scaling won't affect weighting result
        "exponential": lambda x, y: abs(f**x - f**y),
    }[prior]

    def bubble_wrapped_prior_interval_weight(x, y):
        assert x < y
        return prior_interval_weight(x, y)

    prior_interval_expected = {
        # x: interval begin generation, inclusive
        # y: interval end generation, exclusive
        "arbitrary": lambda x, y: statistics.mean((x, y - 1)),
        "uniform": lambda x, y: statistics.mean((x, y - 1)),
        # see
        # https://www.wolframalpha.com/input?i=integrate+f%5Ex+from+a+to+b
        # https://wolframalpha.com/input?i=log%28f%29+%2F+%28f%5Eb+-+f%5Ea%29+times+integral+of+x+*+f%5Ex++from+a+to+b
        # https://www.wolframalpha.com/input?i=b+%2B+%28%28a+-+b%29+f%5Ea%29%2F%28f%5Ea+-+f%5Eb%29+-+1%2Flog%28f%29+with+f+%3D+1.1%2C+a+%3D+10%2C+b%3D14
        "exponential": lambda x, y: (
            (y - 1)
            - 1 / math.log(f)
            + (x - y + 1) * f**x / (f**x - f ** (y - 1))
        )
        if f != 1 and y != x + 1
        else statistics.mean((x, y - 1)),
    }[prior]

    def bubble_wrapped_prior_interval_expected(x, y):
        res = prior_interval_expected(x, y)
        assert x <= res < y
        return res

    return estimator(
        first,
        second,
        prior_interval_weight=bubble_wrapped_prior_interval_weight,
        prior_interval_expected=bubble_wrapped_prior_interval_expected,
    )


def ballpark_rank_of_mrca_between(
    first: HereditaryStratigraphicColumn,
    second: HereditaryStratigraphicColumn,
) -> typing.Optional[float]:
    """Calculate a fast, rough estimate of the rank of the MRCA beteen first
    and second.

    See `estimate_rank_of_mrca_between` for details.
    """

    return estimate_rank_of_mrca_between(
        first,
        second,
        estimator="maximum_likelihood",
        prior="arbitrary",
    )
