from hstrat._auxiliary_lib import collapse_nonleading_whitespace


def test_basic_case():
    assert (
        collapse_nonleading_whitespace("This  is    a test")
        == "This is a test"
    )


def test_leading_whitespace():
    assert (
        collapse_nonleading_whitespace("   Leading   whitespace")
        == "   Leading whitespace"
    )


def test_tabs():
    assert (
        collapse_nonleading_whitespace("Tabs\t\tare\there") == "Tabs are here"
    )


def test_mixed_spaces_and_tabs():
    assert (
        collapse_nonleading_whitespace("Mixed \t spaces  and\t\ttabs")
        == "Mixed spaces and tabs"
    )


def test_multiline_string():
    input_text = "Line one    with spaces\nLine two\t\twith tabs"
    expected_output = "Line one with spaces\nLine two with tabs"
    assert collapse_nonleading_whitespace(input_text) == expected_output


def test_no_changes_needed():
    assert (
        collapse_nonleading_whitespace("No extra spaces") == "No extra spaces"
    )


def test_empty_string():
    assert collapse_nonleading_whitespace("") == ""


def test_only_whitespace():
    assert collapse_nonleading_whitespace("     \t \t  ") == "     \t \t  "
