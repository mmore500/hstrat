import pytest

from hstrat._auxiliary_lib import generate_n


@pytest.fixture
def mock_generator() -> str:
    count = 0

    def generator():
        nonlocal count
        count += 1
        return f"mock data {count - 1}"

    return generator


@pytest.mark.parametrize("n", range(10))
def test_generate_n(mock_generator, n):
    results = [*generate_n(mock_generator, n)]
    assert results == [f"mock data {i}" for i in range(n)]
