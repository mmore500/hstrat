import sys


# adapted from https://medium.com/analytics-vidhya/increase-maximum-recursion-depth-in-python-using-context-manager-1c67eaf4e71b
class RecursionLimit:
    """Context manager to temporarily override recursion limit."""

    def __init__(self, limit):
        self.limit = limit
        self.cur_limit = sys.getrecursionlimit()

    def __enter__(self):
        sys.setrecursionlimit(self.limit)

    def __exit__(self, exc_type, exc_value, exc_traceback):
        sys.setrecursionlimit(self.cur_limit)
