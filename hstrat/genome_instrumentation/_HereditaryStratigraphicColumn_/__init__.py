import opytional as opyt

from ..._auxiliary_lib import hstrat_import_native
from ._HereditaryStratigraphicColumn import HereditaryStratigraphicColumn

impls = [
    HereditaryStratigraphicColumn,
]

HereditaryStratigraphicColumnNative = opyt.apply_if(
    hstrat_import_native("._HereditaryStratigraphicColumnNative", __name__),
    lambda x: x.HereditaryStratigraphicColumnNative,
)
if HereditaryStratigraphicColumnNative is not None:
    impls.append(HereditaryStratigraphicColumnNative)
