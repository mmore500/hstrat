import unittest

from hstrat._auxiliary_lib import omit_last


class TestOmitLast(unittest.TestCase):

    # tests can run independently
    _multiprocess_can_split_ = True

    def test(self):

        for len_ in range(10):
            operand = [*range(len_)]
            assert [*omit_last(operand)] == operand[:-1]
            assert [*omit_last(iter(operand))] == operand[:-1]


if __name__ == "__main__":
    unittest.main()
