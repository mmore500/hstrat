from hstrat import hstrat
from hstrat._auxiliary_lib import get_hstrat_version

def test_version():
    assert hstrat.__version__ == hstrat.get_hstrat_version()
