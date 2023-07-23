"""Tools to load and save hereditary stratigraphic columns."""

from ._assemblage_from_records import assemblage_from_records
from ._col_from_packet import col_from_packet
from ._col_from_records import col_from_records
from ._col_to_dataframe import col_to_dataframe
from ._col_to_packet import col_to_packet
from ._col_to_records import col_to_records
from ._col_to_specimen import col_to_specimen
from ._pack_differentiae import pack_differentiae
from ._pack_differentiae_bytes import pack_differentiae_bytes
from ._pack_differentiae_str import pack_differentiae_str
from ._policy_from_records import policy_from_records
from ._policy_to_records import policy_to_records
from ._pop_from_records import pop_from_records
from ._pop_to_assemblage import pop_to_assemblage
from ._pop_to_dataframe import pop_to_dataframe
from ._pop_to_records import pop_to_records
from ._specimen_from_records import specimen_from_records
from ._unassemblage_from_records import unassemblage_from_records
from ._unpack_differentiae import unpack_differentiae
from ._unpack_differentiae_bytes import unpack_differentiae_bytes
from ._unpack_differentiae_str import unpack_differentiae_str

# adapted from https://stackoverflow.com/a/31079085
__all__ = [
    "assemblage_from_records",
    "col_to_dataframe",
    "col_from_packet",
    "col_from_records",
    "col_to_packet",
    "col_to_records",
    "col_to_specimen",
    "pack_differentiae",
    "pack_differentiae_bytes",
    "pack_differentiae_str",
    "policy_from_records",
    "policy_to_records",
    "pop_from_records",
    "pop_to_assemblage",
    "pop_to_dataframe",
    "pop_to_records",
    "specimen_from_records",
    "unassemblage_from_records",
    "unpack_differentiae",
    "unpack_differentiae_bytes",
    "unpack_differentiae_str",
]

from .._auxiliary_lib import launder_impl_modules as _launder

_launder([eval(item) for item in __all__], __name__)
del _launder  # prevent name from leaking
