import sys


# adapted from https://stackoverflow.com/a/44595269
def is_in_unit_test() -> bool:

    return "pytest" in sys.modules
