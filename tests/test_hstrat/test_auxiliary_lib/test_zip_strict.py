import unittest

from hstrat._auxiliary_lib import zip_strict


class TestZipStrict(unittest.TestCase):

    # tests can run independently
    _multiprocess_can_split_ = True

    def test_none(self):
        assert [*zip_strict()] == [*zip()]

    def test_single(self):
        assert [*zip_strict("")] == [*zip("")]
        assert [*zip_strict("a")] == [*zip("a")]
        assert [*zip_strict("ab")] == [*zip("ab")]

    def test_double(self):
        assert [*zip_strict("", range(0))] == [*zip("", range(0))]
        assert [*zip_strict("a", range(1))] == [*zip("a", range(1))]
        assert [*zip_strict("ab", range(2))] == [*zip("ab", range(2))]

        with self.assertRaises(ValueError):
            for a, b in zip(zip_strict("", range(1)), zip("", range(1))):
                assert a == b

        with self.assertRaises(ValueError):
            for a, b in zip(zip_strict("a", range(0)), zip("a", range(0))):
                assert a == b

        with self.assertRaises(ValueError):
            for a, b in zip(zip_strict("ab", range(1)), zip("ab", range(1))):
                assert a == b

    def test_triple(self):
        assert [*zip_strict("", range(0), [])] == [*zip("", range(0), [])]
        assert [*zip_strict("a", range(1), [None])] == [
            *zip("a", range(1), [None])
        ]
        assert [*zip_strict("ab", range(2), [None, None])] == [
            *zip("ab", range(2), [None, None])
        ]

        with self.assertRaises(ValueError):
            for a, b in zip(
                zip_strict("", range(1), []), zip("", range(1), [])
            ):
                assert a == b

        with self.assertRaises(ValueError):
            for a, b in zip(
                zip_strict("", range(1), [None]), zip("", range(1), [None])
            ):
                assert a == b

        with self.assertRaises(ValueError):
            for a, b in zip(
                zip_strict("a", range(0), [None]), zip("a", range(0), [None])
            ):
                assert a == b

        with self.assertRaises(ValueError):
            for a, b in zip(
                zip_strict("a", range(0), []), zip("a", range(0), [])
            ):
                assert a == b

        with self.assertRaises(ValueError):
            for a, b in zip(
                zip_strict("", range(0), [None]), zip("", range(0), [None])
            ):
                assert a == b

        with self.assertRaises(ValueError):
            for a, b in zip(
                zip_strict("", range(1), [None]), zip("", range(1), [None])
            ):
                assert a == b

        with self.assertRaises(ValueError):
            for a, b in zip(
                zip_strict("ab", range(1), [None, None, None]),
                zip("ab", range(1), [None, None, None]),
            ):
                assert a == b


if __name__ == "__main__":
    unittest.main()
