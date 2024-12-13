from hstrat._auxiliary_lib import textwrap_respect_indents


def test_simple_wrapping():
    text = "This is a simple test to wrap text appropriately."
    result = textwrap_respect_indents(text, ncol=20)
    expected = """This is a simple
test to wrap text
appropriately."""
    assert result == expected


def test_preserve_indentation():
    text = "    Indented line that should respect indentation when wrapped."
    result = textwrap_respect_indents(text, ncol=20)
    expected = """    Indented line
    that should respect
    indentation when
    wrapped."""
    assert result == expected


def test_empty_line_handling():
    text = "First line\n\nThird line"
    result = textwrap_respect_indents(text, ncol=20)
    expected = """First line

Third line"""
    assert result == expected


def test_long_unindented_line():
    text = "ThisIsAVeryLongSingleWordWithoutSpacesThatShouldNotWrap"
    result = textwrap_respect_indents(text, ncol=1000)
    expected = text
    assert result == expected


def test_custom_width():
    text = "Custom width wrapping test."
    result = textwrap_respect_indents(text, ncol=10)
    expected = """Custom
width
wrapping
test."""
    assert result == expected
