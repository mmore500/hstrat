import typing


def reversed_enumerate(
    sequence: typing.Sequence,
) -> typing.Iterable[typing.Tuple[int, object]]:
    """Enumerate a sequence in reverse order.

    This function yields tuples containing the index of each element in the
    sequence and the element itself, with the index values starting from
    the last index in the sequence and counting down to zero.

    Parameters
    ----------
    sequence : typing.Sequence
        The sequence to enumerate.

        Must be sliceable.

    Yields
    -------
    Tuple[int, object]
        A tuple containing the index and element for each item in the
        sequence, in reverse order.

    Examples
    --------
    >>> l = "star"
    >>> list(reversed_enumerate(l))
    [(3, "r"), (2, "a"), (1, "t"), (0, "s")]
    """
    # numba jit doesn't support yield from or reversed (fully)
    for t in zip(range(len(sequence) - 1, -1, -1), sequence[::-1]):
        yield t
