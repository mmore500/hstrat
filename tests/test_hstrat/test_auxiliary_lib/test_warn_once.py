import pytest

from hstrat._auxiliary_lib import warn_once


@pytest.mark.filterwarnings("error")
def test_warn_once():
    msg1 = "asdf"
    msg2 = "hello world"

    # should warn
    with pytest.warns(UserWarning, match=msg1):
        warn_once(msg1)

    # repeat shouldn't warn
    warn_once(msg1)

    # new message should warn
    with pytest.warns(UserWarning, match=msg2):
        warn_once(msg2)
