import types

from .. import _impl_column, _impl_specimen
from ...frozen_instrumentation import HereditaryStratigraphicSpecimen
from ...genome_instrumentation import HereditaryStratigraphicColumn


def dispatch_impl(first: object, second: object) -> types.ModuleType:
    """Return the implementation module corresponding to the input target.

    Parameters
    ----------
    first, second : object
        The target objects for which to obtain the implementation module.
        It can be an instance of HereditaryStratigraphicColumn or
        HereditaryStratigraphicSpecimen.

    Returns
    -------
    types.ModuleType
        The implementation module corresponding to the input target.

    Raises
    ------
    TypeError
        If the input target is not an instance of either
        HereditaryStratigraphicColumn or HereditaryStratigraphicSpecimen.
    """
    assert type(first) == type(second)
    if isinstance(first, HereditaryStratigraphicColumn):
        return _impl_column
    elif isinstance(first, HereditaryStratigraphicSpecimen):
        return _impl_specimen
    else:
        raise TypeError(first)
