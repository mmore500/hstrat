import numpy as np

from hstrat._auxiliary_lib import to_tril


def test_to_tril_square_matrix():
    # Test square matrix input
    matrix = np.array([[1.0, 2.0, 3.0], [4.0, 5.0, 6.0], [7.0, 8.0, 9.0]])
    expected_output = [[0.0], [4.0, 0.0], [7.0, 8.0, 0.0]]
    assert to_tril(matrix) == expected_output


def test_to_tril_non_square_matrix():
    # Test non-square matrix input
    matrix = np.array([[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]])
    expected_output = [[0.0], [4.0, 0.0]]
    assert to_tril(matrix) == expected_output


def test_to_tril_square_matrix_with_zeros():
    # Test square matrix with zeros
    matrix = np.array([[0.0, 0.0, 0.0], [0.0, 0.0, 0.0], [0.0, 0.0, 0.0]])
    expected_output = [[0.0], [0.0, 0.0], [0.0, 0.0, 0.0]]
    assert to_tril(matrix) == expected_output
