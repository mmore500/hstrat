"""Logic to control stratum retention within HereditaryStratigraphicColumn.

Stratum retention policies specify which strata ranks that should be retained ----- and which should be purged --- when the nth stratum is deposited.
Stratum retention algorithms can be parameterized to yield a policy.
"""

from ..._auxiliary_lib import lazy_attach_stub

__getattr__, __dir__, __all__ = lazy_attach_stub(__name__, __file__)
del lazy_attach_stub
