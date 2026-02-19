import functools

from ._alifestd_warn_topological_sensitivity import (
    alifestd_warn_topological_sensitivity,
)


def alifestd_topological_sensitivity_warned(
    *, insert: bool, delete: bool, update: bool
):
    """Decorator that emits a topological sensitivity warning before the
    wrapped function executes.

    The first positional argument of the decorated function must be the
    phylogeny dataframe (pandas).

    Parameters
    ----------
    insert : bool
        Whether the operation inserts new nodes.
    delete : bool
        Whether the operation deletes nodes.
    update : bool
        Whether the operation updates ancestor relationships.

    See Also
    --------
    alifestd_topological_sensitivity_warned_polars :
        Polars-based implementation.
    alifestd_warn_topological_sensitivity :
        Underlying warning function.
    """

    def decorator(func):
        @functools.wraps(func)
        def wrapper(phylogeny_df, *args, **kwargs):
            alifestd_warn_topological_sensitivity(
                phylogeny_df,
                func.__name__,
                insert=insert,
                delete=delete,
                update=update,
            )
            return func(phylogeny_df, *args, **kwargs)

        return wrapper

    return decorator
