import unittest

from hstrat._auxiliary_lib import consume


class TestConsume(unittest.TestCase):

    # tests can run independently
    _multiprocess_can_split_ = True

    def test_iterable(self):
        try:
            consume(range(100))
        except TypeError:
            pass
        else:
            assert False

        try:
            consume([1, 2, 3, 4])
        except TypeError:
            pass
        else:
            assert False

        for n in 0, 1:
            try:
                consume([], n)
            except TypeError:
                pass
            else:
                assert False

    def test_empty(self):
        x = iter([])
        consume(x)
        for __ in x:
            assert False

        for n in 0, 1:
            x = iter(range(0))
            consume(x, n)
            for __ in x:
                assert False

    def test_singleton(self):
        x = iter("a")
        consume(x)
        assert [*x] == []

        x = iter("a")
        consume(x, 0)
        assert [*x] == ["a"]

        for n in 1, 2, 3:
            x = iter(range(1))
            consume(x, n)
            assert [*x] == []

    def test_pair(self):
        x = iter("ab")
        consume(x)
        assert [*x] == []

        x = iter("ab")
        consume(x, 0)
        assert [*x] == ["a", "b"]

        x = iter(range(2))
        consume(x, 1)
        assert [*x] == [1]

        x = iter(range(2))
        consume(x, 2)
        assert [*x] == []

        x = iter(range(2))
        consume(x, 3)
        assert [*x] == []


if __name__ == "__main__":
    unittest.main()
