import logging
import sys
import typing


# adapted from https://github.com/mmore500/joinem/blob/v0.11.1/joinem/_dataframe_cli.py#L120
def eval_kwargs(kwargs_list: typing.List[str]) -> typing.Dict:
    """Parse a list of 'key=value' strings into a dictionary.

    Values are evaluated as Python expressions.

    Parameters
    ----------
    kwargs_list : list of str
        Each element should be a 'key=value' string.

    Returns
    -------
    dict
        Parsed keyword arguments.
    """
    to_eval = f"dict({','.join(kwargs_list)})"
    try:
        return eval(to_eval)
    except Exception as e:
        logging.error(
            "Failed to parse kwarg expressions `%s` via `%s`" " error: %s",
            kwargs_list,
            to_eval,
            e,
        )
        sys.exit(1)
