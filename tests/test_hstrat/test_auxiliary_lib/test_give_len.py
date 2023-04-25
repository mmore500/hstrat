import itertools as it
import unittest

from hstrat._auxiliary_lib import give_len


class TestGiveLen(unittest.TestCase):

    # tests can run independently
    _multiprocess_can_split_ = True

    def test_finite_iterator(self):
        x = give_len(iter(range(10)), 10)
        assert len(x) == 10
        assert [*x] == [*range(10)]

    def test_finite_iterable(self):
        x = give_len(range(10), 12)
        assert len(x) == 12
        assert [*reversed(x)] == [*reversed(range(10))]

    def test_override(self):
        x = give_len("asdf", 42)
        assert len(x) == 42
        assert [*x] == [*"asdf"]
        assert x == "asdf"
        assert "asdf" == x

    def test_infinite_iter(self):
        x = give_len(it.count(4), 101)
        assert len(x) == 101
        assert next(x) == 4


if __name__ == "__main__":
    unittest.main()
