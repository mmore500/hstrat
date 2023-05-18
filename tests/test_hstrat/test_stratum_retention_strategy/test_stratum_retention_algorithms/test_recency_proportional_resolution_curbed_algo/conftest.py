import pytest


def pytest_collection_modifyitems(items):
    for item in items:
        item.add_marker(pytest.mark.filterwarnings("ignore:Size curb set to"))
