import unittest

from hstrat._auxiliary_lib import is_base64

base64_alphabet = """ABCDEFGHIJKLMNOPQRSTUVWXYZ\
abcdefghijklmnopqrstuvwxyz\
0123456789+/"""


class TestBase64(unittest.TestCase):

    # tests can run independently
    _multiprocess_can_split_ = True

    def test_empty(self):

        assert is_base64("")
        assert is_base64(b"")

    def test_str(self):
        assert is_base64(base64_alphabet)
        assert not is_base64("*,.")

    def test_bytes(self):

        assert is_base64(base64_alphabet.encode("ascii"))
        assert is_base64(base64_alphabet.encode("utf_8"))
        assert not is_base64(b"*")

    def test_unicode(self):

        assert not is_base64("😄")
        assert not is_base64("😄".encode("utf_8"))

    def test_not_str_bytes(self):

        self.assertRaises(ValueError, is_base64, 0)
        self.assertRaises(ValueError, is_base64, list(base64_alphabet))
        self.assertRaises(ValueError, is_base64, set(base64_alphabet))


if __name__ == "__main__":
    unittest.main()
