import functools
import typing
import warnings


def except_wrap(
    func: typing.Callable,
    errors: dict[typing.Type[Exception], typing.Optional[str]],
    *,
    sentinel: typing.Any = None
):
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
