#!/bin/python3

from copy import deepcopy
import random
import unittest

from pylib import HereditaryStratum

random.seed(1)

class TestHereditaryStratum(unittest.TestCase):

    def test_deposition_rank(self):
        assert HereditaryStratum(
            deposition_rank=42,
        ).GetDepositionRank() == 42

    def test_uid_generation(self):
        original1 = HereditaryStratum(
            deposition_rank=42,
        )
        copy1 = deepcopy(original1)
        original2 = HereditaryStratum(
            deposition_rank=42,
        )

        assert original1 == copy1
        assert original1 != original2
        assert copy1 != original2

if __name__ == '__main__':
    unittest.main()
