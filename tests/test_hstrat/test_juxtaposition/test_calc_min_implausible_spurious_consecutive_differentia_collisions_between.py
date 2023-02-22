from hstrat import hstrat


def test_calc_min_implausible_spurious_consecutive_differentia_collisions_between():
    assert (
        hstrat.calc_min_implausible_spurious_consecutive_differentia_collisions_between(
            hstrat.HereditaryStratigraphicColumn(
                stratum_differentia_bit_width=1
            ),
            hstrat.HereditaryStratigraphicColumn(
                stratum_differentia_bit_width=1
            ),
            significance_level=0.51,
        )
        == 1
    )
    assert (
        hstrat.calc_min_implausible_spurious_consecutive_differentia_collisions_between(
            hstrat.HereditaryStratigraphicColumn(
                stratum_differentia_bit_width=1
            ),
            hstrat.HereditaryStratigraphicColumn(
                stratum_differentia_bit_width=1
            ),
            significance_level=0.05,
        )
        == 5
    )
    assert (
        hstrat.calc_min_implausible_spurious_consecutive_differentia_collisions_between(
            hstrat.HereditaryStratigraphicColumn(
                stratum_differentia_bit_width=2
            ),
            hstrat.HereditaryStratigraphicColumn(
                stratum_differentia_bit_width=2
            ),
            significance_level=0.05,
        )
        == 3
    )
    assert (
        hstrat.calc_min_implausible_spurious_consecutive_differentia_collisions_between(
            hstrat.HereditaryStratigraphicColumn(
                stratum_differentia_bit_width=5
            ),
            hstrat.HereditaryStratigraphicColumn(
                stratum_differentia_bit_width=5
            ),
            significance_level=0.05,
        )
        == 1
    )
    assert (
        hstrat.calc_min_implausible_spurious_consecutive_differentia_collisions_between(
            hstrat.HereditaryStratigraphicColumn(
                stratum_differentia_bit_width=64
            ),
            hstrat.HereditaryStratigraphicColumn(
                stratum_differentia_bit_width=64
            ),
            significance_level=0.51,
        )
        == 1
    )
    assert (
        hstrat.calc_min_implausible_spurious_consecutive_differentia_collisions_between(
            hstrat.HereditaryStratigraphicColumn(
                stratum_differentia_bit_width=64
            ),
            hstrat.HereditaryStratigraphicColumn(
                stratum_differentia_bit_width=64
            ),
            significance_level=0.05,
        )
        == 1
    )
    assert (
        hstrat.calc_min_implausible_spurious_consecutive_differentia_collisions_between(
            hstrat.HereditaryStratigraphicColumn(
                stratum_differentia_bit_width=64
            ),
            hstrat.HereditaryStratigraphicColumn(
                stratum_differentia_bit_width=64
            ),
            significance_level=0.01,
        )
        == 1
    )
