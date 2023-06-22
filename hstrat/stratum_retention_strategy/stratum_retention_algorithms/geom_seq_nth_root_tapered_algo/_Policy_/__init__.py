import opytional as opyt

from ....._auxiliary_lib import hstrat_import_native
from ._Policy import Policy

impls = [
    Policy,
]

# PolicyNative = opyt.apply_if(
#     hstrat_import_native("._PolicyNative", __name__),
#     lambda x: x.PolicyNative,
# )
# if PolicyNative is not None:
#     impls.append(PolicyNative)
