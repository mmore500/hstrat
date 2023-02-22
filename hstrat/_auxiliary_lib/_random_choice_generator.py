import random
import typing


def random_choice_generator(sequence: typing.Sequence) -> typing.Any:
    """A generator that yields an infinite stream of randomly-selected elements
    from a provided sequence.

    Parameters
    ----------
    sequence : iterable
        The sequence from which to randomly select elements.

    Yields
    ------
    object
        Randomly-selected elements from the sequence.

    Examples
    --------
    >>> stream = random_choice_generator([1, 2, 3])
    >>> next(stream)
    1
    >>> next(stream)
    3
    >>> next(stream)
    2
    >>> next(stream)
    1
    >>> next(stream)
    3
    >>> next(stream)
    2
    """
    while True:
        yield random.choice(sequence)
