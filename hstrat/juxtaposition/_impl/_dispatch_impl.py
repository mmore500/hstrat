import types
import typing

from .. import _impl_column, _impl_specimen
from ...frozen_instrumentation import (
    HereditaryStratigraphicSpecimen,
    HereditaryStratigraphicAssemblageSpecimen,
)
from ...genome_instrumentation import HereditaryStratigraphicColumn


def dispatch_impl(target: object) -> types.ModuleType:
    """Return the implementation module corresponding to the input target.

    Parameters
    ----------
    target : object
        The target object for which to obtain the implementation module.
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
    if isinstance(target, HereditaryStratigraphicColumn):
        return _impl_column
    elif isinstance(target, HereditaryStratigraphicSpecimen):
        return _impl_specimen
    else:
        raise TypeError(target)
