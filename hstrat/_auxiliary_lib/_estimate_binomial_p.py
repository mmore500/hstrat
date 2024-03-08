import itertools as it
import typing

import numpy as np
import statsmodels.api as sm


def estimate_binomial_p(
    sampler: typing.Callable,
    confidence: float = 0.99,
    precision: float = 0.01,
    progress_wrap: typing.Callable = lambda x: x,
) -> typing.Tuple[float, typing.Tuple[float, float, int]]:
    """Estimate the probability of success in a binomial distribution, along
    with a confidence interval.

    This function uses a given sampler to generate observations, estimating the
    probability of success. It continues sampling until the width of the
    confidence interval is less than or equal to the specified precision.

    Parameters
    ----------
    sampler : typing.Callable
        A no-argument function that returns a boolean indicating success (True)
        or failure (False) for each trial.
    confidence : float, optional
        The confidence level for the confidence interval of the estimated
        probability, by default 0.99.
    precision : float, optional
        The desired precision of the confidence interval (the maximum
        acceptable width of the interval), by default 0.01.

    Returns
    -------
    typing.Tuple[float, typing.Tuple[float, float], int]
        A tuple containing the estimated probability of success, the
        confidence interval (lower bound, upper bound), and the number of
        observations taken.

    Notes
    -----
    The estimation uses the Wilson score interval for calculating the
    confidence interval of the proportion.

    Examples
    --------
    >>> def coin_flip_sampler():
    ...     return np.random.choice([True, False])
    ...
    >>> p_estimate, conf_interval = estimate_binomial_p(coin_flip_sampler)
    """
    num_success = 0
    for num_observed in progress_wrap(it.count(start=1)):
        num_success += bool(sampler())
        confint = sm.stats.proportion_confint(
            count=num_success,
            nobs=num_observed,
            alpha=1 - confidence,
            method="wilson",
        )
        uncertainty = np.ptp(confint)
        if uncertainty <= precision:
            break

    return num_success / num_observed, confint, num_observed
