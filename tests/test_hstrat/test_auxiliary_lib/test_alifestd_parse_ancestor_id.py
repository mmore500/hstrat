import unittest

from hstrat._auxiliary_lib import alifestd_parse_ancestor_id


class TestOmitLast(unittest.TestCase):

    # tests can run independently
    _multiprocess_can_split_ = True

    def test_empty(self):
        assert alifestd_parse_ancestor_id("[]") is None
        assert alifestd_parse_ancestor_id("[None]") is None
        assert alifestd_parse_ancestor_id("[none]") is None
        assert alifestd_parse_ancestor_id("[NONE]") is None

    def test_singleton(self):
        assert alifestd_parse_ancestor_id("[1]") == 1
        assert alifestd_parse_ancestor_id("[12]") == 12
        assert alifestd_parse_ancestor_id("[0]") == 0
        assert alifestd_parse_ancestor_id("[1289]") == 1289


if __name__ == "__main__":
    unittest.main()
