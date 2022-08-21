import itertools as it
import unittest

from hstrat._auxiliary_lib import all_same


class TestAllSame(unittest.TestCase):

    # tests can run independently
    _multiprocess_can_split_ = True

    def test_empty(self):
        for container in list, dict, set, iter:
            assert all_same(container(()))

    def test_singleton(self):
        for container in list, iter:
            for content in None, True, False, "a", 1, 0, "asdf", [1, 2, 3]:
                assert all_same(container((content,)))

        for container in (set,):
            for hashable_content in None, True, False, "a", 1, 0, "asdf":
                assert all_same(container((hashable_content,)))

    def test_doublet_same(self):
        for container in list, iter:
            for content in None, True, False, "a", 1, 0, "asdf", [1, 2, 3]:
                assert all_same(container((content, content)))

        for container in (set,):
            for hashable_content in None, True, False, "a", 1, 0, "asdf":
                assert all_same(
                    container((hashable_content, hashable_content))
                )

    def test_doublet_notsame(self):
        content = None, True, False, "a", 1, 0, "asdf", [1, 2, 3]
        for container in list, iter:
            for a, b in it.permutations(content, 2):
                assert all_same(container((a, b))) == (a == b)

        hashable_content = None, True, False, "a", 1, 0, "asdf"
        for container in (set,):
            for a, b in it.permutations(hashable_content, 2):
                assert all_same(container((a, b))) == (a == b)

    def test_triplet_same(self):
        for container in list, iter:
            for content in None, True, False, "a", 1, 0, "asdf", [1, 2, 3]:
                assert all_same(container((content, content, content)))

        for container in (set,):
            for hashable_content in None, True, False, "a", 1, 0, "asdf":
                assert all_same(
                    container(
                        (
                            hashable_content,
                            hashable_content,
                            hashable_content,
                        )
                    )
                )

    def test_triplet_onenotsame(self):
        content = None, True, False, "a", 1, 0, "asdf", [1, 2, 3]
        for container in list, iter:
            for a, b in it.permutations(content, 2):
                assert all_same(container((a, b, a))) == (a == b)
                assert all_same(container((a, a, b))) == (a == b)

        hashable_content = None, True, False, "a", 1, 0, "asdf"
        for container in (set,):
            for a, b in it.permutations(hashable_content, 2):
                assert all_same(container((a, b, a))) == (a == b)
                assert all_same(container((a, a, b))) == (a == b)

    def test_triplet_allnotsame(self):
        content = None, True, False, "a", 1, 0, "asdf", [1, 2, 3]
        for container in list, iter:
            for a, b, c in it.permutations(content, 3):
                assert all_same(container((a, b, c))) == (a == b == c)

        hashable_content = None, True, False, "a", 1, 0, "asdf"
        for container in (set,):
            for a, b, c in it.permutations(hashable_content, 3):
                assert all_same(container((a, b, c))) == (a == b == c)


if __name__ == "__main__":
    unittest.main()
