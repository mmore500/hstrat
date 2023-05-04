import typing

from ._with_omission import with_omission


def generate_omission_subsets(
    sequence: typing.Sequence,
) -> typing.Iterator[typing.Iterator]:
    """Generate all possible single-omission subsets of an input sequence, with
    the kth element omitted from the kth subset.

    Parameters
    ----------
    sequence : sequence
        The input sequence to generate subsets from.

    Yields
    ------
    iterable
        An iterable of the input sequence with one element omitted.

    Examples
    --------
    >>> list(generate_omission_subsets([1, 2, 3]))
    [[2, 3], [1, 3], [1, 2]]

    >>> list(generate_omission_subsets('abc'))
    [['b', 'c'], ['a', 'c'], ['a', 'b']]
    """
    for index, __ in enumerate(sequence):
        yield with_omission(sequence, index)
