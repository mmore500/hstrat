import functools
import typing
import warnings


def except_wrap_sentinel(
    func: typing.Callable,
    errors: dict[typing.Type[Exception], typing.Optional[str]],
    *,
    sentinel: typing.Any = None,
) -> typing.Callable:
    """Decorator to catch specified exceptions and return a sentinel value.

    Parameters
    ----------
    func : callable
        The function to wrap.
    errors : dict of Exception to str or None
        A mapping of exception types to optional warning messages. If the
        function raises one of these exceptions, that exception will be caught.
        If a message is provided, a warning will be issued. If no message is
        provided (None), no warning will be issued.
    sentinel : object, optional
        The value to return if any of the specified exceptions is raised, by
        default None.

    Returns
    -------
    callable
        A wrapped version of `func`. When called, if `func` raises one of the
        exceptions listed in `errors`, `sentinel` will be returned instead, and
        a warning may be issued if specified.
    """

    @functools.wraps(func)
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            for err_type, message in errors.items():
                if isinstance(e, err_type):
                    if message is not None:
                        warnings.warn(message)
                    return sentinel
            raise e

    return inner
