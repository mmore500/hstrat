import itertools as it
import random

import pytest

from hstrat import hstrat


@pytest.mark.parametrize(
    "confidence_level",
    [0.8, 0.95, 0.99],
)
@pytest.mark.parametrize(
    "differentia_bit_width",
    [1, 2, 8, 64],
)
def test_CalcRanksSinceEarliestDetectableMrcaWith1(
    confidence_level,
    differentia_bit_width,
):
    expected_thresh = (
        hstrat.HereditaryStratigraphicColumn(
            stratum_differentia_bit_width=differentia_bit_width,
        ).CalcMinImplausibleSpuriousConsecutiveDifferentiaCollisions(
            significance_level=1 - confidence_level,
        )
        - 1
    )

    for r1, r2, r3 in it.product(*[range(1, expected_thresh)] * 3):
        c1 = hstrat.HereditaryStratigraphicColumn(
            stratum_differentia_bit_width=differentia_bit_width,
            stratum_retention_policy=hstrat.perfect_resolution_algo.Policy(),
        )
        c2 = c1.Clone()
        c3 = hstrat.HereditaryStratigraphicColumn(
            stratum_differentia_bit_width=differentia_bit_width,
            stratum_retention_policy=hstrat.fixed_resolution_algo.Policy(2),
        )
        for __ in range(r1 - 1):
            c1.DepositStratum()
        for __ in range(r2 - 1):
            c2.DepositStratum()
        for __ in range(r3 - 1):
            c3.DepositStratum()

        for x1, x2 in it.combinations([c1, c2, c3], 2):
            assert (
                x1.CalcRanksSinceEarliestDetectableMrcaWith(
                    x2,
                    confidence_level=confidence_level,
                )
                is None
            ), (
                r1,
                r2,
                r3,
                confidence_level,
                differentia_bit_width,
                x1.CalcRanksSinceEarliestDetectableMrcaWith(
                    x2,
                    confidence_level=confidence_level,
                ),
                x1.GetNumStrataRetained(),
                x2.GetNumStrataRetained(),
            )
            assert (
                x2.CalcRanksSinceEarliestDetectableMrcaWith(
                    x1,
                    confidence_level=confidence_level,
                )
                is None
            )
            assert (
                x1.CalcRankOfMrcaBoundsWith(
                    x2,
                    confidence_level=confidence_level,
                )
                is None
            )
            assert (
                x2.CalcRankOfMrcaBoundsWith(
                    x1,
                    confidence_level=confidence_level,
                )
                is None
            )


@pytest.mark.parametrize(
    "confidence_level",
    [0.8, 0.95, 0.99],
)
@pytest.mark.parametrize(
    "differentia_bit_width",
    [1, 2, 8, 64],
)
def test_CalcRanksSinceEarliestDetectableMrcaWith2(
    confidence_level,
    differentia_bit_width,
):
    expected_thresh = (
        hstrat.HereditaryStratigraphicColumn(
            stratum_differentia_bit_width=differentia_bit_width,
        ).CalcMinImplausibleSpuriousConsecutiveDifferentiaCollisions(
            significance_level=1 - confidence_level,
        )
        - 1
    )

    c1 = hstrat.HereditaryStratigraphicColumn(
        stratum_differentia_bit_width=differentia_bit_width,
        stratum_retention_policy=hstrat.perfect_resolution_algo.Policy(),
    )
    c2 = c1.Clone()
    c3 = hstrat.HereditaryStratigraphicColumn(
        stratum_differentia_bit_width=differentia_bit_width,
        stratum_retention_policy=hstrat.fixed_resolution_algo.Policy(2),
    )

    for x1, x2 in it.combinations([c1, c2, c3], 2):
        x1 = x1.Clone()
        x2 = x2.Clone()
        while x1.GetNthCommonRankWith(x2, expected_thresh) is None:
            random.choice([x1, x2]).DepositStratum()

        assert x1.CalcRanksSinceEarliestDetectableMrcaWith(
            x2,
            confidence_level=confidence_level,
        ) == (
            x1.GetNumStrataDeposited()
            - x1.GetNthCommonRankWith(x2, expected_thresh)
            - 1
        )
        assert x2.CalcRanksSinceEarliestDetectableMrcaWith(
            x1,
            confidence_level=confidence_level,
        ) == (
            x2.GetNumStrataDeposited()
            - x2.GetNthCommonRankWith(x2, expected_thresh)
            - 1
        )

        for __ in range(3):
            x1.DepositStratum()
            x2.DepositStratum()

        assert x1.CalcRanksSinceEarliestDetectableMrcaWith(
            x2,
            confidence_level=confidence_level,
        ) == (
            x1.GetNumStrataDeposited()
            - x1.GetNthCommonRankWith(x2, expected_thresh)
            - 1
        )
        assert x2.CalcRanksSinceEarliestDetectableMrcaWith(
            x1,
            confidence_level=confidence_level,
        ) == (
            x2.GetNumStrataDeposited()
            - x2.GetNthCommonRankWith(x2, expected_thresh)
            - 1
        )
