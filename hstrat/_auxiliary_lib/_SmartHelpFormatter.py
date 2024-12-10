import argparse


def leading_whitespace(line: str) -> int:
    """Counts the leading whitespace of `line`, treating tabs as 4 spaces"""
    prefix = line[: len(line) - len(line.lstrip())]
    return len(prefix) + 3 * prefix.count("\t")


# https://stackoverflow.com/a/76962505
class SmartHelpFormatter(argparse.HelpFormatter):
    """
    A custom HelpFormatter that allows one to pass in a formatted description
    for the `--help` message that contains possible newlines.
    """

    def _split_lines(self, text: str, width: int):
        r = []
        for line in text.split("\n"):
            n = leading_whitespace(line)
            r.extend(
                " " * n + s for s in super()._split_lines(line, width - n)
            )
        return r

    def _fill_text(self, text: str, width: int, indent: str):
        r = []
        for line in text.splitlines():
            n = leading_whitespace(line)
            r.append(super()._fill_text(line, width, indent + " " * n))
        return "\n".join(r)
