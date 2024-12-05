import numbers
import typing
import warnings

import numpy as np


def cast_int_lossless(
    value: numbers.Real,
    action: typing.Literal["warn", "raise"],
    context: str = "",
) -> int:
    """Cast a real number to an integer, with options to warn or raise an
    exception if the conversion involves precision loss.

    Parameters
    ----------
    value : numbers.Real
        Real number to be converted to an integer.
    action : {'warn', 'raise'}
        Action to take if the conversion results in precision loss.
    context : str, optional
        Additional context to include in the warning or error message.

    Returns
    -------
    int
        The integer value after conversion.

    Raises
    ------
    ValueError
        If `action` is 'raise' and the conversion results in precision loss.
    RuntimeError
        If `action` is unrecognized.

    Examples
    --------
    >>> coerce_int_warn_lossy(3.14, 'warn', 'example')
    UserWarning: Precision loss in example conversion of 3.14 to int.
    3

    >>> coerce_int_warn_lossy(3.14, 'raise')
    ValueError: Precision loss in conversion of 3.14 to int.
    """

    if not np.isclose(value, int(value)):
        message = (
            "Precision loss in"
            + f" {context}".rstrip()
            + f" conversion of {value} to int."
        )
        if action == "warn":
            warnings.warn(message)
        elif action == "raise":
            raise ValueError(message)
        else:
            raise RuntimeError(f"action {action} is unrecognized")

    return int(value)
