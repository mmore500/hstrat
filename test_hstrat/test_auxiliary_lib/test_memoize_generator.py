import itertools as it
import unittest

from hstrat._auxiliary_lib import memoize_generator


class TestMemoizeGenerator(unittest.TestCase):

    # tests can run independently
    _multiprocess_can_split_ = True

    def test_empty(self):
        @memoize_generator()
        def empty_generator(*args, **kwargs):
            return
            yield

        assert [*empty_generator()] == []
        assert [*empty_generator()] == []
        assert [*empty_generator(1)] == []
        assert [*empty_generator(2)] == []

    def test_singleton(self):
        @memoize_generator()
        def singleton_generator(item):
            yield item

        assert [*singleton_generator("a")] == ["a"]
        assert [*singleton_generator("b")] == ["b"]
        assert [*singleton_generator("a")] == ["a"]
        assert [*singleton_generator("a")] == ["a"]

    def test_infinite(self):
        @memoize_generator()
        def infinite_generator(i):
            for x in it.count(i):
                yield x

        assert [*it.islice(infinite_generator(0), 3)] == [*range(3)]
        assert [*it.islice(infinite_generator(0), 2)] == [*range(2)]
        assert [*it.islice(infinite_generator(1), 2)] == [*range(1, 3)]


if __name__ == "__main__":
    unittest.main()
