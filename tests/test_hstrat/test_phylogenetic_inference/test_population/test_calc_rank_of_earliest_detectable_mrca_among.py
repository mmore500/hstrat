import itertools as it
import random

import pytest

from hstrat import hstrat


@pytest.mark.filterwarnings(
    "ignore:Insufficient common ranks between columns to detect common ancestry at given confidence level."
)
@pytest.mark.parametrize(
    "confidence_level",
    [0.8, 0.95, 0.99],
)
@pytest.mark.parametrize(
    "differentia_bit_width",
    [1, 2, 8, 64],
)
@pytest.mark.parametrize(
    "wrap",
    [lambda x: x, hstrat.col_to_specimen],
)
def test_calc_rank_of_earliest_detectable_mrca_among1(
    confidence_level,
    differentia_bit_width,
    wrap,
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
                hstrat.calc_rank_of_earliest_detectable_mrca_among(
                    [wrap(x1), wrap(x2)],
                    confidence_level=confidence_level,
                )
                is None
            )
            assert (
                hstrat.calc_rank_of_earliest_detectable_mrca_among(
                    [wrap(x2), wrap(x1)],
                    confidence_level=confidence_level,
                )
                is None
            )
            assert (
                hstrat.calc_rank_of_earliest_detectable_mrca_among(
                    [wrap(x1), wrap(x2), wrap(x1)],
                    confidence_level=confidence_level,
                )
                is None
            )
            assert (
                hstrat.calc_rank_of_earliest_detectable_mrca_among(
                    [wrap(x2), wrap(x1)] * 10,
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
@pytest.mark.parametrize(
    "wrap",
    [lambda x: x, hstrat.col_to_specimen],
)
def test_calc_rank_of_earliest_detectable_mrca_among2(
    confidence_level,
    differentia_bit_width,
    wrap,
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
        while (
            hstrat.get_nth_common_rank_between(x1, x2, expected_thresh) is None
        ):
            random.choice([x1, x2]).DepositStratum()

        assert hstrat.calc_rank_of_earliest_detectable_mrca_among(
            [wrap(x1), wrap(x2)],
            confidence_level=confidence_level,
        ) == hstrat.get_nth_common_rank_between(x1, x2, expected_thresh)
        assert hstrat.calc_rank_of_earliest_detectable_mrca_among(
            [wrap(x2), wrap(x1)],
            confidence_level=confidence_level,
        ) == hstrat.get_nth_common_rank_between(x2, x1, expected_thresh)
        assert hstrat.calc_rank_of_earliest_detectable_mrca_among(
            [wrap(x1), wrap(x2), wrap(x1)],
            confidence_level=confidence_level,
        ) == hstrat.get_nth_common_rank_between(x1, x2, expected_thresh)
        assert hstrat.calc_rank_of_earliest_detectable_mrca_among(
            [wrap(x2), wrap(x1)] * 10,
            confidence_level=confidence_level,
        ) == hstrat.get_nth_common_rank_between(x2, x1, expected_thresh)

        for __ in range(3):
            x1.DepositStratum()
            x2.DepositStratum()

        assert hstrat.calc_rank_of_earliest_detectable_mrca_among(
            [wrap(x1), wrap(x2)],
            confidence_level=confidence_level,
        ) == hstrat.get_nth_common_rank_between(x1, x2, expected_thresh)
        assert hstrat.calc_rank_of_earliest_detectable_mrca_among(
            [wrap(x2), wrap(x1)],
            confidence_level=confidence_level,
        ) == hstrat.get_nth_common_rank_between(x2, x1, expected_thresh)
        assert hstrat.calc_rank_of_earliest_detectable_mrca_among(
            [wrap(x1), wrap(x2), wrap(x1)],
            confidence_level=confidence_level,
        ) == hstrat.get_nth_common_rank_between(x1, x2, expected_thresh)
        assert hstrat.calc_rank_of_earliest_detectable_mrca_among(
            [wrap(x2), wrap(x1)] * 10,
            confidence_level=confidence_level,
        ) == hstrat.get_nth_common_rank_between(x2, x1, expected_thresh)


@pytest.mark.parametrize(
    "wrap",
    [lambda x: x, hstrat.col_to_specimen],
)
def test_calc_rank_of_earliest_detectable_mrca_among3(wrap):

    c1 = hstrat.HereditaryStratigraphicColumn(
        stratum_differentia_bit_width=64,
        stratum_retention_policy=hstrat.perfect_resolution_algo.Policy(),
    )
    for __ in range(10):
        assert (
            hstrat.calc_rank_of_earliest_detectable_mrca_among(
                [wrap(c1), wrap(c1)]
            )
            == 0
        )
        assert (
            hstrat.calc_rank_of_earliest_detectable_mrca_among(
                [wrap(c1), wrap(c1)] * 10
            )
            == 0
        )
        c1.DepositStratum()


@pytest.mark.filterwarnings("ignore:Empty or singleton population.")
@pytest.mark.parametrize(
    "wrap",
    [lambda x: x, hstrat.col_to_specimen],
)
def test_calc_rank_of_earliest_detectable_mrca_among4(wrap):

    c1 = hstrat.HereditaryStratigraphicColumn(
        stratum_differentia_bit_width=64,
        stratum_retention_policy=hstrat.perfect_resolution_algo.Policy(),
    )
    for __ in range(10):
        assert (
            hstrat.calc_rank_of_earliest_detectable_mrca_among([wrap(c1)])
            is None
        )
        assert hstrat.calc_rank_of_earliest_detectable_mrca_among([]) is None
        c1.DepositStratum()


@pytest.mark.parametrize(
    "wrap",
    [lambda x: x, hstrat.col_to_specimen],
)
def test_calc_rank_of_earliest_detectable_mrca_among_generator(wrap):
    c1 = hstrat.HereditaryStratigraphicColumn(
        stratum_differentia_bit_width=1,
    )
    for __ in range(10):
        assert hstrat.calc_rank_of_earliest_detectable_mrca_among(
            [wrap(c1) for __ in range(10)]
        ) == hstrat.calc_rank_of_earliest_detectable_mrca_among(
            (wrap(c1) for __ in range(10))
        )
        c1.DepositStratum()

    c2 = hstrat.HereditaryStratigraphicColumn(
        stratum_differentia_bit_width=64,
    )
    for __ in range(10):
        assert hstrat.calc_rank_of_earliest_detectable_mrca_among(
            [wrap(c2) for __ in range(10)]
        ) == hstrat.calc_rank_of_earliest_detectable_mrca_among(
            (wrap(c2) for __ in range(10))
        )
        c2.DepositStratum()
