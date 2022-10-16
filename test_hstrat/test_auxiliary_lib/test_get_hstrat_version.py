import hstrat
from hstrat._auxiliary_lib import get_hstrat_version


def test_get_hstrat_version():
    assert get_hstrat_version() == hstrat.__version__
