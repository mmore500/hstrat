from hstrat._auxiliary_lib import is_in


def test_is_in_true():
    data = [1, 2, 3]
    assert is_in(data, [data, [4, 5, 6], [7, 8, 9]]) == True


def test_is_in_false():
    data = [1, 2, 3]
    assert is_in(data, [[4, 5, 6], [7, 8, 9]]) == False


def test_is_in_empty_iterator():
    data = {"a": 1, "b": 2}
    assert is_in(data, []) == False


def test_is_in_identical_objects():
    data = [1, 2, 3]
    assert is_in(data, [data.copy(), [4, 5, 6], [7, 8, 9]]) == False
