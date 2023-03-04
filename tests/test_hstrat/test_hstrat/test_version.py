from hstrat import hstrat


def test_version():
    assert hstrat.__version__ == hstrat.get_hstrat_version()
