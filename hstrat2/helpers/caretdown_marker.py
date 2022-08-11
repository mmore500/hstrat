import typing

caretdown_marker: typing.List[typing.Tuple[int, int]] = [
    (0, 0),
    (-1, 3**0.5),
    (1, 3**0.5),
    (0, 0),
]
"""A equilateral triangle, oriented tip down and positioned within the
encapsulating unit cell so that it appears just above the coordinates it is
placed at.

Equivalent to matplotlib "CARETDOWN" marker, except that it is a closed path so
edge outline will appear properly.
"""
