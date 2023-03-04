import typing

from ._RngStateContext import RngStateContext


def with_rng_state_context(seed: int) -> typing.Callable:
    """Decorator to set the random number generator state before calling a
    function.

    The pre-existing random number generator state is restored when the
    decorated function returns.

    Parameters
    ----------
    seed : int
        The seed to use for the random number generator.

    Returns
    -------
    typing.Callable
        A callable that takes a function as its argument and returns a
        decorated function.

    Examples
    --------
    >>> import random
    >>> @with_rng_state_context(seed=123)
    ... def my_function():
    ...     return random.random()
    ...
    >>> my_function() == my_function()
    True
    """

    def decorator(func: typing.Callable) -> typing.Callable:
        """Decorate a function to set the random number generator state.

        Parameters
        ----------
        func : typing.Callable
            The function to be decorated.

        Returns
        -------
        typing.Callable
            The decorated function.
        """

        def wrapper(*args, **kwargs):
            """Wrapper function that sets the random number generator state
            before calling the decorated function.

            Parameters
            ----------
            args : list
                The positional arguments to pass to the decorated function.
            kwargs : dict
                The keyword arguments to pass to the decorated function.

            Returns
            -------
            The return value of the decorated function.
            """
            with RngStateContext(seed):
                return func(*args, **kwargs)

        return wrapper

    return decorator
