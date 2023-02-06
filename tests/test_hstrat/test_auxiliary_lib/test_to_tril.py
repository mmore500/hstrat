import numpy as np

from hstrat._auxiliary_lib import to_tril

def test_to_tril_square_matrix():
    # Test square matrix input
    matrix = np.array([[1., 2., 3.], [4., 5., 6.], [7., 8., 9.]])
    expected_output = [[ 0.], [4., 0.], [7., 8., 0.]]
    assert to_tril(matrix) == expected_output


def test_to_tril_non_square_matrix():
    # Test non-square matrix input
    matrix = np.array([[1., 2., 3.], [4., 5., 6.]])
    expected_output = [[ 0.], [4., 0.]]


def test_to_tril_square_matrix_with_zeros():
    # Test square matrix with zeros
    matrix = np.array([[0., 0., 0.], [0., 0., 0.], [0., 0., 0.]])
    expected_output = [[ 0.], [0., 0.], [0., 0., 0.]]
    assert to_tril(matrix) == expected_output
