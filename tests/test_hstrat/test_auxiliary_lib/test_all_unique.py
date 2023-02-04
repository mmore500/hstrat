import itertools as it
import unittest

import numpy as np

from hstrat._auxiliary_lib import all_unique


class TestAllUnique(unittest.TestCase):

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

            assert (num_unique == len(test_arr)) == all_unique(test_arr)


if __name__ == "__main__":
    unittest.main()
