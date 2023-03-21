import math
import statistics

import numpy as np
import pytest

from hstrat import hstrat


def test_calc_interval_probability_proxy():
    prior = hstrat.UniformPrior()
    assert math.isclose(
        prior.CalcIntervalProbabilityProxy(0, 100),
        prior.CalcIntervalProbabilityProxy(0, 50)
        + prior.CalcIntervalProbabilityProxy(50, 100),
    )
    assert math.isclose(
        prior.CalcIntervalProbabilityProxy(89, 100),
        prior.CalcIntervalProbabilityProxy(89, 91)
        + prior.CalcIntervalProbabilityProxy(91, 100),
    )

    assert (
        pytest.approx(
            prior.CalcIntervalProbabilityProxy(99, 100)
            / prior.CalcIntervalProbabilityProxy(0, 1)
        )
        == 1
    )

    assert (
        pytest.approx(
            prior.CalcIntervalProbabilityProxy(42, 43)
            / prior.CalcIntervalProbabilityProxy(0, 2)
        )
        == 0.5
    )

    assert (
        pytest.approx(
            prior.CalcIntervalProbabilityProxy(99, 100)
            / prior.CalcIntervalProbabilityProxy(7, 8)
        )
        == 1
    )

    assert (
        pytest.approx(
            prior.CalcIntervalProbabilityProxy(42, 43)
            / prior.CalcIntervalProbabilityProxy(9, 11)
        )
        == 0.5
    )


def test_calc_interval_conditioned_mean():
    prior = hstrat.UniformPrior()
    begin, end = 0, 100
    interval_width = 1

    intervals = [
        (interval_begin, interval_begin + interval_width)
        for interval_begin in range(begin, end, interval_width)
    ]

    samples = np.array(
        [
            statistics.mean((interval_begin, interval_end - 1))
            for interval_begin, interval_end in intervals
        ]
    )
    weights = np.array(
        [
            prior.CalcIntervalProbabilityProxy(interval_begin, interval_end)
            for interval_begin, interval_end in intervals
        ]
    )

    assert math.isclose(
        np.average(samples, weights=weights),
        prior.CalcIntervalConditionedMean(begin, end),
    )
