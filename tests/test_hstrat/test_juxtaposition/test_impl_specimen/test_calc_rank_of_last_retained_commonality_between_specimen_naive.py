import random
from unittest.mock import MagicMock

import contexttimer as ctt
import numpy as np
import pytest

from hstrat import hstrat
from hstrat.juxtaposition._impl_column import (
    calc_rank_of_last_retained_commonality_between_generic,
)
from hstrat.juxtaposition._impl_specimen import (
    calc_rank_of_last_retained_commonality_between,
)


@pytest.fixture
def specimens_mock_simple():
    # Create example HereditaryStratigraphicAssemblageSpecimen instances
    # with known values for testing.
    first = MagicMock()
    second = MagicMock()
    first.GetStratumDifferentiaBitWidth.return_value = 8
    second.GetStratumDifferentiaBitWidth.return_value = 8
    first.GetDifferentiaVals.return_value = np.array([5, 6, 7, 8, 9])
    second.GetDifferentiaVals.return_value = np.array([5, 6, 7, 8, 9])
    first.GetNumStrataRetained.return_value = 5
    second.GetNumStrataRetained.return_value = 5
    first.GetNumStrataDeposited.return_value = 5
    second.GetNumStrataDeposited.return_value = 5
    first.GetRankIndex.return_value = np.array([0, 1, 2, 3, 4])
    second.GetRankIndex.return_value = np.array([0, 1, 2, 3, 4])
    return first, second


def test_calc_rank_of_last_retained_commonality_between_mock_simple(
    specimens_mock_simple,
):
    first, second = specimens_mock_simple

    # Test case where there is no disparity.
    assert (
        calc_rank_of_last_retained_commonality_between(
            first, second, confidence_level=0.49
        )
        == 4
    )
    assert (
        calc_rank_of_last_retained_commonality_between(
            first, second, confidence_level=0.9999999999999
        )
        is None
    )

    # Test case where there is disparity.
    second.GetDifferentiaVals.return_value = np.array([5, 6, 3, 8, 9])
    assert (
        calc_rank_of_last_retained_commonality_between(
            first, second, confidence_level=0.49
        )
        == 1
    )


@pytest.fixture
def specimens_mock_complex():
    # Create example HereditaryStratigraphicAssemblageSpecimen instances
    # with known values for testing.
    first = MagicMock()
    second = MagicMock()
    first.GetStratumDifferentiaBitWidth.return_value = 8
    second.GetStratumDifferentiaBitWidth.return_value = 8
    first.GetDifferentiaVals.return_value = np.array([5, 6, 7, 8, 9])
    second.GetDifferentiaVals.return_value = np.array([5, 42, 9, 202])
    first.GetNumStrataRetained.return_value = 5
    second.GetNumStrataRetained.return_value = 4
    first.GetNumStrataDeposited.return_value = 5
    second.GetNumStrataDeposited.return_value = 6
    first.GetRankIndex.return_value = np.array([0, 10, 20, 30, 40])
    second.GetRankIndex.return_value = np.array([0, 20, 40, 50])
    return first, second


def test_calc_rank_of_last_retained_commonality_between_mock_complex(
    specimens_mock_complex,
):
    first, second = specimens_mock_complex

    assert (
        calc_rank_of_last_retained_commonality_between(
            first, second, confidence_level=0.49
        )
        == 0
    )

    assert (
        calc_rank_of_last_retained_commonality_between(
            first, second, confidence_level=0.999
        )
        is None
    )


@pytest.mark.filterwarnings(
    "ignore:Insufficient common ranks between columns to detect common ancestry at given confidence level."
)
@pytest.mark.parametrize(
    "retention_policy",
    [
        hstrat.nominal_resolution_algo.Policy(),
        hstrat.fixed_resolution_algo.Policy(fixed_resolution=7),
        hstrat.recency_proportional_resolution_algo.Policy(
            recency_proportional_resolution=2,
        ),
        hstrat.recency_proportional_resolution_algo.Policy(
            recency_proportional_resolution=10,
        ),
    ],
)
@pytest.mark.parametrize(
    "differentia_width",
    [1, 2, 8, 64, 65],
)
@pytest.mark.parametrize(
    "confidence_level",
    [0.49, 0.8, 0.95, 0.9999],
)
@pytest.mark.parametrize(
    "uneven_branches",
    [True, False],
)
@pytest.mark.parametrize(
    "other_pop_member",
    [True, False],
)
def test_compare_to_generic_column_impl(
    retention_policy,
    differentia_width,
    confidence_level,
    uneven_branches,
    other_pop_member,
):
    common_ancestors = [
        hstrat.HereditaryStratigraphicColumn(
            stratum_differentia_bit_width=differentia_width,
            stratum_retention_policy=retention_policy,
        )
    ]
    for __ in range(37):
        common_ancestors.append(common_ancestors[-1].CloneDescendant())

    for _rep in range(250):
        _ = _rep
        num_total = random.randrange(0, 37)

        num_together = random.randrange(num_total + 1)
        assert 0 <= num_together <= num_total
        num_alone = num_total - num_together

        left_alone = num_alone
        right_alone = num_alone

        common_ancestor = common_ancestors[num_together]
        left = common_ancestor.Clone()
        right = common_ancestor.Clone()

        left.DepositStrata(left_alone)
        right.DepositStrata(
            right_alone + uneven_branches * random.randrange(0, 37)
        )

        pop = [left, right]
        if other_pop_member:
            pop.append(
                random.choice(common_ancestors).CloneNthDescendant(
                    random.randrange(0, 63)
                )
            )
        specimen1, specimen2, *__ = map(hstrat.col_to_specimen, pop)

        assert (
            specimen1.GetNumStrataDeposited() == left.GetNumStrataDeposited()
        )
        assert specimen1.GetNumStrataRetained() == left.GetNumStrataRetained()
        assert (
            specimen2.GetNumStrataDeposited() == right.GetNumStrataDeposited()
        )
        assert specimen2.GetNumStrataRetained() == right.GetNumStrataRetained()

        assert calc_rank_of_last_retained_commonality_between(
            specimen1, specimen2, confidence_level=confidence_level
        ) == calc_rank_of_last_retained_commonality_between_generic(
            left, right, confidence_level=confidence_level
        )


def test_benchmark():
    common_ancestor = hstrat.HereditaryStratigraphicColumn(
        stratum_differentia_bit_width=8,
        stratum_retention_policy=hstrat.recency_proportional_resolution_algo.Policy(
            recency_proportional_resolution=10
        ),
    ).CloneNthDescendant(100000)

    tip1_c = common_ancestor.CloneNthDescendant(100000)
    tip2_c = common_ancestor.CloneNthDescendant(90000)

    tip1_s = hstrat.col_to_specimen(tip1_c)
    tip2_s = hstrat.col_to_specimen(tip2_c)

    # pre-compile jit outside of timing
    calc_rank_of_last_retained_commonality_between(
        tip1_s,
        tip2_s,
        confidence_level=0.9999,
    )

    with ctt.Timer(factor=1000) as t_algo_dstruct:
        for __ in range(10000):
            calc_rank_of_last_retained_commonality_between(
                tip1_s,
                tip2_s,
                confidence_level=0.9999,
            )

    # note higher factor and lower repcount
    with ctt.Timer(factor=10000) as t_dstruct:
        for __ in range(1000):
            calc_rank_of_last_retained_commonality_between_generic(
                tip1_s,
                tip2_s,
                confidence_level=0.9999,
            )

    with ctt.Timer(factor=1000) as t_vanilla:
        for __ in range(10000):
            calc_rank_of_last_retained_commonality_between_generic(
                tip1_c,
                tip2_c,
                confidence_level=0.9999,
            )

    print(f"t_algo_dstruct={t_algo_dstruct}")
    print(f"t_dstruct={t_dstruct} ")
    print(f"t_vanilla={t_vanilla}")
