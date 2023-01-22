import itertools as it
import unittest

import numpy as np

from hstrat._auxiliary_lib import count_unique


class TestCountUnique(unittest.TestCase):

    # tests can run independently
    _multiprocess_can_split_ = True

    def test(self):

        for num_unique, num_duplications, shuffle, in it.product(
            np.arange(10),
            np.arange(1, 10),
            [True, False],
        ):
            test_arr = np.array(
                [
                    val
                    for val in range(num_unique)
                    for __ in range(num_duplications)
                ]
            )

            if shuffle:
                np.random.shuffle(test_arr)

            assert count_unique(test_arr) == num_unique


if __name__ == "__main__":
    unittest.main()
