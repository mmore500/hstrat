from hstrat import hstrat


def test_calc_probability_differentia_collision_between():
    assert (
        hstrat.calc_probability_differentia_collision_between(
            hstrat.HereditaryStratigraphicColumn(
                stratum_differentia_bit_width=1
            ),
            hstrat.HereditaryStratigraphicColumn(
                stratum_differentia_bit_width=1
            ),
        )
        == 0.5
    )
    assert (
        hstrat.calc_probability_differentia_collision_between(
            hstrat.HereditaryStratigraphicColumn(
                stratum_differentia_bit_width=2
            ),
            hstrat.HereditaryStratigraphicColumn(
                stratum_differentia_bit_width=2
            ),
        )
        == 0.25
    )
    assert (
        hstrat.calc_probability_differentia_collision_between(
            hstrat.HereditaryStratigraphicColumn(
                stratum_differentia_bit_width=3
            ),
            hstrat.HereditaryStratigraphicColumn(
                stratum_differentia_bit_width=3
            ),
        )
        == 0.125
    )
    assert (
        hstrat.calc_probability_differentia_collision_between(
            hstrat.HereditaryStratigraphicColumn(
                stratum_differentia_bit_width=8
            ),
            hstrat.HereditaryStratigraphicColumn(
                stratum_differentia_bit_width=8
            ),
        )
        == 1.0 / 256.0
    )
