import math
import statistics

import numpy as np
import pytest

from hstrat import hstrat
import hstrat.phylogenetic_inference.priors._detail as detail


def test_base_class():
    assert issubclass(hstrat.ArbitraryPrior, detail.PriorBase)


def test_calc_interval_probability_proxy():
    prior = hstrat.ArbitraryPrior()

    assert (
        len(
            {
                prior.CalcIntervalProbabilityProxy(0, 50),
                prior.CalcIntervalProbabilityProxy(7, 8),
                prior.CalcIntervalProbabilityProxy(99, 100),
                prior.CalcIntervalProbabilityProxy(78, 100),
            }
        )
        == 1
    )


@pytest.mark.parametrize(
    "interval_width",
    [1, 2, 3],
)
def test_calc_interval_conditioned_mean(interval_width):
    prior = hstrat.ArbitraryPrior()
    begin, end = 0, 10000

    # required for arbitrary prior due to arbitraryness
    end -= end % interval_width

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


def test_sample_interval_conditioned_value():
    prior = hstrat.ArbitraryPrior()
    samples = set(
        prior.SampleIntervalConditionedValue(0, 100) for _ in range(100)
    )
    assert len(samples) > 1
    assert all(0 <= sample < 100 for sample in samples)
