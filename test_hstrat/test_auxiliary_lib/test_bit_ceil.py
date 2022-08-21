import unittest

from hstrat._auxiliary_lib import bit_ceil


class TestBitCeil(unittest.TestCase):

    # tests can run independently
    _multiprocess_can_split_ = True

    def test(self):
        assert bit_ceil(0b00000000) == 0b00000001
        assert bit_ceil(0b00000001) == 0b00000001
        assert bit_ceil(0b00000010) == 0b00000010
        assert bit_ceil(0b00000011) == 0b00000100
        assert bit_ceil(0b00000100) == 0b00000100
        assert bit_ceil(0b00000101) == 0b00001000
        assert bit_ceil(0b00000110) == 0b00001000
        assert bit_ceil(0b00000111) == 0b00001000
        assert bit_ceil(0b00001000) == 0b00001000
        assert bit_ceil(0b00001001) == 0b00010000


if __name__ == "__main__":
    unittest.main()
