import pytest

from hstrat import hstrat
from hstrat.phylogenetic_inference.priors._BubbleWrappedPrior import (
    BubbleWrappedPrior,
)
import hstrat.phylogenetic_inference.priors._detail as detail


def test_base_class():
    assert issubclass(BubbleWrappedPrior, detail.PriorBase)


def test_calc_interval_probability_proxy():
    wrapee = hstrat.ArbitraryPrior()
    wrapped = BubbleWrappedPrior(wrapee)
    for params in (0, 50), (7, 8), (99, 100), (78, 100):
        assert wrapped.CalcIntervalProbabilityProxy(
            *params
        ) == wrapee.CalcIntervalProbabilityProxy(*params)

    with pytest.raises(AssertionError):
        wrapped.CalcIntervalProbabilityProxy(7, 7)
        wrapped.CalcIntervalProbabilityProxy(42, 41)
        wrapped.CalcIntervalProbabilityProxy(-1, 41)


def test_calc_interval_conditioned_mean():
    wrapee = hstrat.ArbitraryPrior()
    wrapped = BubbleWrappedPrior(wrapee)
    for params in (0, 50), (7, 8), (99, 100), (78, 100):
        assert wrapped.CalcIntervalConditionedMean(
            *params
        ) == wrapee.CalcIntervalConditionedMean(*params)

    with pytest.raises(AssertionError):
        wrapped.CalcIntervalConditionedMean(7, 7)
        wrapped.CalcIntervalConditionedMean(42, 41)
        wrapped.CalcIntervalConditionedMean(-1, 41)


def test_sample_interval_conditioned_value():
    wrapee = hstrat.ArbitraryPrior()
    wrapped = BubbleWrappedPrior(wrapee)
    with pytest.raises(NotImplementedError):
        wrapped.SampleIntervalConditionedValue(0, 100)
