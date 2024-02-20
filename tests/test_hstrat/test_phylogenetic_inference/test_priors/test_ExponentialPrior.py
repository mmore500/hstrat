import math

import numpy as np
import pytest

from hstrat import hstrat
import hstrat.phylogenetic_inference.priors._detail as detail


def test_base_class():
    assert issubclass(hstrat.ExponentialPrior, detail.PriorBase)


@pytest.mark.parametrize(
    "growth_factor",
    [
        1.0,
        1.0000001,
        1.000001,
        1.0001,
        1.01,
        1.5,
    ],
)
def test_calc_interval_probability_proxy(growth_factor):
    prior = hstrat.ExponentialPrior(growth_factor)
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
        == growth_factor**99
    )

    assert (
        pytest.approx(
            prior.CalcIntervalProbabilityProxy(42, 43)
            / prior.CalcIntervalProbabilityProxy(1, 2)
        )
        == growth_factor**41
    )
    assert prior.CalcIntervalProbabilityProxy(0, 1) >= 0


@pytest.mark.parametrize(
    "interval_width",
    [1, 2],
)
@pytest.mark.parametrize(
    "growth_factor",
    [1.0, 1.0000001, 1.01, 1.05],
)
def test_calc_interval_conditioned_mean(interval_width, growth_factor):
    prior = hstrat.ExponentialPrior(growth_factor)
    begin, end = 0, 10000

    intervals = [
        (interval_begin, interval_begin + interval_width)
        for interval_begin in range(begin, end, interval_width)
    ]

    samples = np.array(
        [
            # interval_begin
            prior.CalcIntervalConditionedMean(interval_begin, interval_end)
            for interval_begin, interval_end in intervals
        ]
    )
    weights = np.array(
        [
            prior.CalcIntervalProbabilityProxy(interval_begin, interval_end)
            for interval_begin, interval_end in intervals
        ]
    )

    # some discretization bias is expected
    assert np.average(samples, weights=weights) == pytest.approx(
        prior.CalcIntervalConditionedMean(begin, end), abs=0.5
    )
    assert 0 <= prior.CalcIntervalConditionedMean(0, 1) <= 1


def test_sample_interval_conditioned_value():
    with pytest.raises(NotImplementedError):
        hstrat.ExponentialPrior(1.0).SampleIntervalConditionedValue(0, 100)
