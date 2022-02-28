import unittest

from hstrat.helpers import attach_attrs


class TestAttachAttrs(unittest.TestCase):

    # tests can run independently
    _multiprocess_can_split_ = True

    def test_routine(self):
        @attach_attrs({
            'foo' : 'bar',
            'qux' : 42,
        },)
        def routine():
            return 64

        assert routine() == 64
        assert routine.foo == 'bar'
        assert routine.qux == 42

    def test_function(self):
        @attach_attrs({
            'foo' : 'bar',
            'qux' : 42,
        },)
        def function(*args, **kwargs,):
            return 128

        assert function('fish', bip='bop',) == 128
        assert function.foo == 'bar'
        assert function.qux == 42


if __name__ == '__main__':
    unittest.main()
