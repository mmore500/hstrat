from hstrat._auxiliary_lib import capitalize_n


def test_capitalize_n_empty_string():
    assert capitalize_n("", 0) == ""
    assert capitalize_n("", 1) == ""
    assert capitalize_n("", 2) == ""


def test_capitalize_n_capitalize_all():
    assert capitalize_n("hello world", 11) == "HELLO WORLD"
    assert capitalize_n("goodbye", 7) == "GOODBYE"
    assert capitalize_n("testing", 7) == "TESTING"
    assert capitalize_n("12345", 5) == "12345"


def test_capitalize_n_capitalize_none():
    assert capitalize_n("hello world", 0) == "hello world"
    assert capitalize_n("goodbye", 0) == "goodbye"
    assert capitalize_n("testing", 0) == "testing"


def test_capitalize_n_capitalize_partial():
    assert capitalize_n("hello world", 5) == "HELLO world"
    assert capitalize_n("goodbye", 2) == "GOodbye"
    assert capitalize_n("testing", 3) == "TESting"


def test_capitalize_n_capitalize_negative():
    assert capitalize_n("hello world", -5) == "hello WORLD"
    assert capitalize_n("testing", -1) == "testinG"
