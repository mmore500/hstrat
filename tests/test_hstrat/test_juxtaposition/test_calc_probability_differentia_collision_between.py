import pytest

from hstrat import hstrat


@pytest.mark.parametrize(
    "wrap",
    [lambda x: x, hstrat.col_to_specimen],
)
def test_calc_probability_differentia_collision_between(wrap):
    assert (
        hstrat.calc_probability_differentia_collision_between(
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
        )
        == 0.5
    )
    assert (
        hstrat.calc_probability_differentia_collision_between(
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
        )
        == 0.25
    )
    assert (
        hstrat.calc_probability_differentia_collision_between(
            wrap(
                hstrat.HereditaryStratigraphicColumn(
                    stratum_differentia_bit_width=3
                )
            ),
            wrap(
                hstrat.HereditaryStratigraphicColumn(
                    stratum_differentia_bit_width=3
                )
            ),
        )
        == 0.125
    )
    assert (
        hstrat.calc_probability_differentia_collision_between(
            wrap(
                hstrat.HereditaryStratigraphicColumn(
                    stratum_differentia_bit_width=8
                )
            ),
            wrap(
                hstrat.HereditaryStratigraphicColumn(
                    stratum_differentia_bit_width=8
                )
            ),
        )
        == 1.0 / 256.0
    )
