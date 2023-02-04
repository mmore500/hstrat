import sys


# adapted from https://stackoverflow.com/a/44595269
def is_in_unit_test() -> bool:
    """Is current execution within a unit testing context?

    Can be used to enable more thorough assert checks than desired in normal
    (i.e., non-optimized) mode outside testing context.
    """
    return "pytest" in sys.modules
