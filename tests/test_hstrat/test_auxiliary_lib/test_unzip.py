from hstrat._auxiliary_lib import unzip


def test_unzip_with_two_element_tuples():
    input_iterable = [(1, 2), (3, 4), (5, 6)]
    expected_output = [(1, 3, 5), (2, 4, 6)]
    assert list(unzip(input_iterable)) == expected_output


def test_unzip_with_three_element_tuples():
    input_iterable = [(1, 2, 3), (4, 5, 6)]
    expected_output = [(1, 4), (2, 5), (3, 6)]
    assert list(unzip(input_iterable)) == expected_output


def test_unzip_with_one_element_tuples():
    input_iterable = [(1,), (2,), (3,)]
    expected_output = [
        (1, 2, 3),
    ]
    assert list(unzip(input_iterable)) == expected_output


def test_unzip_with_empty_tuples():
    input_iterable = [(), (), ()]
    expected_output = []
    assert list(unzip(input_iterable)) == expected_output


def test_unzip_with_empty():
    input_iterable = []
    expected_output = []
    assert list(unzip(input_iterable)) == expected_output
