"""Tools to load and save hereditary stratigraphic columns."""

from ._col_to_dataframe import col_to_dataframe
from ._col_from_records import col_from_records
from ._col_to_records import col_to_records
from ._pack_differentiae import pack_differentiae
from ._pop_from_records import pop_from_records
from ._pop_to_records import pop_to_records
from ._unpack_differentiae import unpack_differentiae

# adapted from https://stackoverflow.com/a/31079085
__all__ = [
    "col_to_dataframe",
    "col_from_records",
    "col_to_records",
    "pack_differentiae",
    "pop_from_records",
    "pop_to_records",
    "unpack_differentiae",
]

from .._auxiliary_lib import launder_impl_modules as _launder

_launder([eval(item) for item in __all__], __name__)
del _launder  # prevent name from leaking
