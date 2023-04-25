from hstrat._auxiliary_lib import deep_listify, generate_omission_subsets


def test_generate_omission_subsets_with_list():
    assert deep_listify(generate_omission_subsets([1, 2, 3])) == [
        [2, 3],
        [1, 3],
        [1, 2],
    ]


def test_generate_omission_subsets_with_tuple():
    assert deep_listify(generate_omission_subsets((4, 5, 6))) == [
        [5, 6],
        [4, 6],
        [4, 5],
    ]


def test_generate_omission_subsets_with_string():
    assert deep_listify(generate_omission_subsets("ab")) == [["b"], ["a"]]


def test_generate_omission_subsets_with_empty_sequence():
    assert deep_listify(generate_omission_subsets([])) == []
