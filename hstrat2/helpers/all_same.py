import typing


# Adapted from https://stackoverflow.com/a/3787989
def all_same(items: typing.Iterable) -> bool:
    """Do all items in items compare equal?

    Returns True if items is empty.
    """
    it = iter(items)

    for first in it:
        break
    else:
        return True  # empty case, note all([]) is True

    return all(x == first for x in it)
