import math
import typing

from ...genome_instrumentation import HereditaryStratigraphicColumn
from ..priors import ArbitraryPrior, UniformPrior
from ..priors._BubbleWrappedPrior import BubbleWrappedPrior
from ._impl import (
    estimate_rank_of_mrca_maximum_likelihood,
    estimate_rank_of_mrca_naive,
    estimate_rank_of_mrca_unbiased,
)


def estimate_rank_of_mrca_between(
    first: HereditaryStratigraphicColumn,
    second: HereditaryStratigraphicColumn,
    estimator: str,
    prior: typing.Union[str, typing.Any],
) -> typing.Optional[float]:
    """At what generation did the most recent common ancestor of first and
    second occur?

    Parameters
    ----------
    estimator : {"maximum_likelihood", "unbiased"}
        What estimation method should be used? Options are "maximum_likelihood"
        or "unbiased".

        The "maximum_likelihood" estimator is faster to compute than the
        "unbiased" estimator.
    prior : {"arbitrary", "uniform"} or object implementing prior interface
        Prior probability density distribution over possible generations of the
        MRCA.

        Implementations for arbitrary, geometric, exponential, and uniform
        priors are available in hstrat.phylogenetic_inference.priors. User
        -defined classes specifying custom priors can also be provided.

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

    if isinstance(prior, str):
        prior = {
            "arbitrary": ArbitraryPrior,
            "uniform": UniformPrior,
        }[prior]()

    res = estimator(
        first,
        second,
        prior=BubbleWrappedPrior(prior),
    )
    if res is not None:
        assert 0 <= res or math.isclose(0, res, abs_tol=10e-6), res
        max = (
            min(first.GetNumStrataDeposited(), second.GetNumStrataDeposited())
            - 1
        )
        assert res <= max or math.isclose(res, max), (res, max)
    return res


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
