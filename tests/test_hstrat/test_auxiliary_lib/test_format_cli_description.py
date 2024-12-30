from hstrat._auxiliary_lib import format_cli_description


def test_smoke():
    assert "asdf" in format_cli_description("asdf")
    assert "hello" in format_cli_description(
        """
hello.

world!
    1. one
    2. two
    3. three
"""
    )
