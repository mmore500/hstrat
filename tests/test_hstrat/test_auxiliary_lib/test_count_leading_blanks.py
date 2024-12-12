from hstrat._auxiliary_lib import count_leading_blanks


def test_no_leading_blanks():
    assert count_leading_blanks("hello") == 0


def test_with_leading_blanks():
    assert count_leading_blanks("   hello") == 3


def test_only_blanks():
    assert count_leading_blanks("     ") == 5


def test_empty_string():
    assert count_leading_blanks("") == 0


def test_mixed_whitespace_characters():
    assert count_leading_blanks("\t  hello") == 3  # Assuming tabs count as one


def test_tabs_only():
    assert count_leading_blanks("\t\t\t") == 3  # Assuming tabs count as one


def test_no_leading_but_trailing_whitespace():
    assert count_leading_blanks("hello   ") == 0
