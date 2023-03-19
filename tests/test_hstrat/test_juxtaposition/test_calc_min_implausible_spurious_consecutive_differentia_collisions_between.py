import pytest

from hstrat import hstrat


@pytest.mark.parametrize(
    "wrap",
    [lambda x: x, hstrat.col_to_specimen],
)
def test_calc_min_implausible_spurious_consecutive_differentia_collisions_between(
    wrap,
):
    assert (
        hstrat.calc_min_implausible_spurious_consecutive_differentia_collisions_between(
            wrap(
                hstrat.HereditaryStratigraphicColumn(
                    stratum_differentia_bit_width=1
                )
            ),
            wrap(
                hstrat.HereditaryStratigraphicColumn(
                    stratum_differentia_bit_width=1
                )
            ),
            significance_level=0.51,
        )
        == 1
    )
    assert (
        hstrat.calc_min_implausible_spurious_consecutive_differentia_collisions_between(
            wrap(
                hstrat.HereditaryStratigraphicColumn(
                    stratum_differentia_bit_width=1
                )
            ),
            wrap(
                hstrat.HereditaryStratigraphicColumn(
                    stratum_differentia_bit_width=1
                )
            ),
            significance_level=0.05,
        )
        == 5
    )
    assert (
        hstrat.calc_min_implausible_spurious_consecutive_differentia_collisions_between(
            wrap(
                hstrat.HereditaryStratigraphicColumn(
                    stratum_differentia_bit_width=2
                )
            ),
            wrap(
                hstrat.HereditaryStratigraphicColumn(
                    stratum_differentia_bit_width=2
                )
            ),
            significance_level=0.05,
        )
        == 3
    )
    assert (
        hstrat.calc_min_implausible_spurious_consecutive_differentia_collisions_between(
            wrap(
                hstrat.HereditaryStratigraphicColumn(
                    stratum_differentia_bit_width=5
                )
            ),
            wrap(
                hstrat.HereditaryStratigraphicColumn(
                    stratum_differentia_bit_width=5
                )
            ),
            significance_level=0.05,
        )
        == 1
    )
    assert (
        hstrat.calc_min_implausible_spurious_consecutive_differentia_collisions_between(
            wrap(
                hstrat.HereditaryStratigraphicColumn(
                    stratum_differentia_bit_width=64
                )
            ),
            wrap(
                hstrat.HereditaryStratigraphicColumn(
                    stratum_differentia_bit_width=64
                )
            ),
            significance_level=0.51,
        )
        == 1
    )
    assert (
        hstrat.calc_min_implausible_spurious_consecutive_differentia_collisions_between(
            wrap(
                hstrat.HereditaryStratigraphicColumn(
                    stratum_differentia_bit_width=64
                )
            ),
            wrap(
                hstrat.HereditaryStratigraphicColumn(
                    stratum_differentia_bit_width=64
                )
            ),
            significance_level=0.05,
        )
        == 1
    )
    assert (
        hstrat.calc_min_implausible_spurious_consecutive_differentia_collisions_between(
            wrap(
                hstrat.HereditaryStratigraphicColumn(
                    stratum_differentia_bit_width=64
                )
            ),
            wrap(
                hstrat.HereditaryStratigraphicColumn(
                    stratum_differentia_bit_width=64
                )
            ),
            significance_level=0.01,
        )
        == 1
    )
