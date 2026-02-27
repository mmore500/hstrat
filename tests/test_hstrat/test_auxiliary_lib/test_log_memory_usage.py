import os

import more_itertools as mit
import pytest

from hstrat._auxiliary_lib import log_memory_usage


@pytest.fixture(autouse=True)
def _set_log_memory_env(monkeypatch):
    monkeypatch.setenv("HSTRAT_LOG_MEMORY_USAGE", "1")


def test_log_memory_usage():
    message = []
    log_memory_usage(message.append)
    assert "available" in mit.one(message)


def test_log_memory_usage_disabled(monkeypatch):
    monkeypatch.delenv("HSTRAT_LOG_MEMORY_USAGE", raising=False)
    message = []
    log_memory_usage(message.append)
    assert len(message) == 0
