import itertools as it
import unittest

from hstrat._auxiliary_lib import pairwise


class TestAllSame(unittest.TestCase):

    # tests can run independently
    _multiprocess_can_split_ = True

    def test_empty(self):
        for container in list, dict, set, iter:
            assert [*pairwise(container(()))] == []

    def test_singleton(self):
        for container in list, iter:
            for content in None, True, False, "a", 1, 0, "asdf", [1, 2, 3]:
                assert [*pairwise(container((content,)))] == []

    def test_different_types(self):
        for container in list, iter:
            content = [None, True, False, "a", [1, 2, 3]]
            assert [*pairwise(container(content))] == [
                (None, True),
                (True, False),
                (False, "a"),
                ("a", [1, 2, 3]),
            ]

    def test_doublet_same(self):
        for container in list, iter:
            for content in None, True, False, "a", 1, 0, "asdf", [1, 2, 3]:
                assert [*pairwise(container((content, content)))] == [
                    (content, content),
                ]

    def test_doublet_notsame(self):
        content = None, True, False, "a", 1, 0, "asdf", [1, 2, 3]
        for container in list, iter:
            for a, b in it.permutations(content, 2):
                assert [*pairwise(container((a, b)))] == [
                    (a, b),
                ]

    def test_triplet_same(self):
        for container in list, iter:
            for content in None, True, False, "a", 1, 0, "asdf", [1, 2, 3]:
                assert [*pairwise(container((content, content, content)))] == [
                    (content, content),
                    (content, content),
                ]

    def test_same_type(self):
        for container in list, iter:
            content = range(4)
            assert [*pairwise(container(content))] == [
                (0, 1),
                (1, 2),
                (2, 3),
            ]


if __name__ == "__main__":
    unittest.main()
