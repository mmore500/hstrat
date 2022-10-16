"""Tools to load and save hereditary stratigraphic columns."""

from ._pack_differentiae import pack_differentiae
from ._unpack_differentiae import unpack_differentiae

# adapted from https://stackoverflow.com/a/31079085
__all__ = [
    "pack_differentiae",
    "unpack_differentiae",
]

from .._auxiliary_lib import launder_impl_modules as _launder

_launder([eval(item) for item in __all__], __name__)
del _launder  # prevent name from leaking
