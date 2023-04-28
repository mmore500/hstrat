import pytest

from hstrat._auxiliary_lib import best_effort_lexicographical_compare


@pytest.mark.parametrize(
    "first, second, expected",
    [
        ([1, 2, 3], [1, None, 2], False),
        ([1, None, 2], [1, 2, 3], True),
        ([1, 2, 3], [1, 2], False),
        ([1, 2], [1, 2, None], True),
        ([], [], False),
        ([1], [], False),
        ([None], [], False),
        ([], [None], True),
        ([], [1], True),
        ([1, 2], [1, "2"], False),
        ([1, 2], [1, "2", 3], True),
        ([1, 2, 3], [1, "2"], False),
        ([1, 2, 3], [1, "2", 4], True),
        ([1, 2], "12", False),
        ("12", [1, 2], False),
        ([None], [1, 2], True),
        ([1, 2], [None], False),
        ([1, 2], [1, 2], False),
    ],
)
def test_best_effort_lexicographical_compare(first, second, expected):
    assert best_effort_lexicographical_compare(first, second) == expected
