import opytional as opyt

from ....._auxiliary_lib import hstrat_import_native
from ._PolicySpec import PolicySpec

impls = [
    PolicySpec,
]

# PolicySpecNative = opyt.apply_if(
#     hstrat_import_native("._PolicySpecNative", __name__),
#     lambda x: x.PolicySpecNative,
# )
# if PolicySpecNative is not None:
#     impls.append(PolicySpecNative)
