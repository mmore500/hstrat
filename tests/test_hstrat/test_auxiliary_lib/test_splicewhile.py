import unittest

from hstrat._auxiliary_lib import splicewhile


class TestConsume(unittest.TestCase):

    # tests can run independently
    _multiprocess_can_split_ = True

    def test_iterable(self):
        for condition in True, False:
            try:
                splicewhile(lambda x: condition, range(100))
            except TypeError:
                pass
            else:
                assert False

            try:
                splicewhile(lambda x: condition, [1, 2, 3, 4])
            except TypeError:
                pass
            else:
                assert False

            try:
                splicewhile(lambda x: condition, [])
            except TypeError:
                pass
            else:
                assert False

    def test_empty(self):
        for condition in True, False:
            it = iter([])
            res, it = splicewhile(lambda x: condition, it)
            assert res == []
            for __ in it:
                assert False

        for condition in True, False:
            it = iter(range(0))
            res, it = splicewhile(lambda x: condition, it)
            for __ in it:
                assert False

    def test_singleton(self):
        it = iter("a")
        res, it = splicewhile(lambda x: x == "a", it)
        assert res == ["a"]
        assert [*it] == []

        it = iter("a")
        res, it = splicewhile(lambda x: x != "a", it)
        assert res == []
        assert [*it] == ["a"]

        for n in 1, 2, 3:
            it = iter(range(1))
            res, it = splicewhile(lambda x: x < n, it)
            assert res == [0]
            assert [*it] == []

    def test_conservation(self):
        for n in range(20):
            for cut in range(n + 1):
                it = iter(range(n))
                res, it = splicewhile(lambda x: x != cut, it)
                rest = [*it]
                assert res == [*range(cut)]
                assert res + rest == [*range(n)]


if __name__ == "__main__":
    unittest.main()
