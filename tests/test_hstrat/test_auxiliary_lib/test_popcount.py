from hstrat._auxiliary_lib import popcount


def test_popcount():
    assert popcount(0) == 0
    assert popcount(1) == 1
    assert popcount(2) == 1
    assert popcount(3) == 2
    assert popcount(4) == 1
    assert popcount(5) == 2
    assert popcount(6) == 2
    assert popcount(7) == 3
    assert popcount(12481027492184092184390812949318513097509831) == 76
