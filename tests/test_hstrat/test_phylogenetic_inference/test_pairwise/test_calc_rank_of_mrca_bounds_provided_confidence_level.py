from hstrat import hstrat


def test_CalcRankOfMrcaBoundsProvidedConfidenceLevel():
    c1 = hstrat.HereditaryStratigraphicColumn(
        stratum_differentia_bit_width=1,
    )
    assert (
        hstrat.calc_rank_of_mrca_bounds_provided_confidence_level(c1, c1, 0.5)
        == 0.5
    )
    assert (
        hstrat.calc_rank_of_mrca_bounds_provided_confidence_level(c1, c1, 0.6)
        == 0.75
    )
    assert (
        hstrat.calc_rank_of_mrca_bounds_provided_confidence_level(c1, c1, 0.75)
        == 0.75
    )

    c2 = hstrat.HereditaryStratigraphicColumn(
        stratum_differentia_bit_width=64,
    )
    p = 1 / 2**64
    assert (
        hstrat.calc_rank_of_mrca_bounds_provided_confidence_level(c2, c2, 0.5)
        == 1 - p
    )
    assert (
        hstrat.calc_rank_of_mrca_bounds_provided_confidence_level(c2, c2, 0.6)
        == 1 - p
    )
    assert (
        hstrat.calc_rank_of_mrca_bounds_provided_confidence_level(c2, c2, 0.75)
        == 1 - p
    )
    assert (
        hstrat.calc_rank_of_mrca_bounds_provided_confidence_level(c2, c2, 0.95)
        == 1 - p
    )
    assert (
        hstrat.calc_rank_of_mrca_bounds_provided_confidence_level(c2, c2, 0.99)
        == 1 - p
    )
