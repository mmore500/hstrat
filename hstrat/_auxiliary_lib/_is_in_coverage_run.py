import sys


# adapted from https://stackoverflow.com/a/69531314
# alternate approach: https://stackoverflow.com/a/69531314
def is_in_coverage_run() -> bool:
    """Is code coverage currently being measured?"""
    return "coverage" in sys.modules
