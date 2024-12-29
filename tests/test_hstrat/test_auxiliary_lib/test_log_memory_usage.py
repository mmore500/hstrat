import more_itertools as mit

from hstrat._auxiliary_lib import log_memory_usage


def test_log_memory_usage():
    message = []
    log_memory_usage(message.append)
    assert "available" in mit.one(message)
