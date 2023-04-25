import unittest

from hstrat._auxiliary_lib import alifestd_parse_ancestor_ids


class TestOmitLast(unittest.TestCase):

    # tests can run independently
    _multiprocess_can_split_ = True

    def test_empty(self):
        assert alifestd_parse_ancestor_ids("[]") == []
        assert alifestd_parse_ancestor_ids("[None]") == []
        assert alifestd_parse_ancestor_ids("[none]") == []
        assert alifestd_parse_ancestor_ids("[NONE]") == []

    def test_singleton(self):
        assert alifestd_parse_ancestor_ids("[1]") == [1]
        assert alifestd_parse_ancestor_ids("[12]") == [12]
        assert alifestd_parse_ancestor_ids("[0]") == [0]

    def test_double(self):
        assert alifestd_parse_ancestor_ids("[1,12]") == [1, 12]
        assert alifestd_parse_ancestor_ids("[12,1]") == [12, 1]
        assert alifestd_parse_ancestor_ids("[0,1]") == [0, 1]

        assert alifestd_parse_ancestor_ids("[1, 0]") == [1, 0]
        assert alifestd_parse_ancestor_ids("[12, 1]") == [12, 1]
        assert alifestd_parse_ancestor_ids("[0, 1]") == [0, 1]

    def test_triple(self):
        assert alifestd_parse_ancestor_ids("[1,12,128]") == [1, 12, 128]
        assert alifestd_parse_ancestor_ids("[12,1, 0]") == [12, 1, 0]
        assert alifestd_parse_ancestor_ids("[0, 1,143]") == [0, 1, 143]
        assert alifestd_parse_ancestor_ids("[1, 0, 199]") == [1, 0, 199]


if __name__ == "__main__":
    unittest.main()
