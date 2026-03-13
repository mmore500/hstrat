"""Patch phyloframe functions for pandas 3 compatibility.

Pandas 3 enables Copy-on-Write by default, causing ``.to_numpy()`` to
return readonly arrays.  Phyloframe's numba-JIT functions write to input
arrays, which fails with readonly arrays.  This module patches the
affected phyloframe functions to copy arrays before passing them to numba.
"""

import functools
import typing

import numpy as np


def _writable_jit_wrapper(jit_func: typing.Callable) -> typing.Callable:
    """Wrap a numba JIT function to ensure all array arguments are writable."""

    @functools.wraps(jit_func)
    def wrapper(*args, **kwargs):
        args = tuple(
            np.require(a, requirements="W") if isinstance(a, np.ndarray) else a
            for a in args
        )
        return jit_func(*args, **kwargs)

    return wrapper


def patch_phyloframe() -> None:
    """Apply pandas 3 compatibility patches to phyloframe.legacy.

    Patches numba JIT-compiled functions that write to input numpy arrays,
    ensuring the arrays are writable under pandas 3's Copy-on-Write mode.
    """
    import pandas as pd

    if int(pd.__version__.split(".")[0]) < 3:
        return  # no patches needed for pandas 2

    try:
        import phyloframe.legacy._alifestd_collapse_unifurcations as _cu
    except ImportError:
        return

    if not getattr(_cu, "_hstrat_patched", False):
        _cu._collapse_unifurcations = _writable_jit_wrapper(
            _cu._collapse_unifurcations,
        )
        _cu._hstrat_patched = True

    try:
        import phyloframe.legacy._alifestd_reroot_at_id_asexual as _rr
    except ImportError:
        return

    if not getattr(_rr, "_hstrat_patched", False):
        # The reroot function writes directly to .to_numpy() arrays
        # in non-JIT code. Wrap the public function to reconstruct
        # the DataFrame with writable arrays.
        _orig_reroot = _rr.alifestd_reroot_at_id_asexual

        @functools.wraps(_orig_reroot)
        def _patched_reroot(phylogeny_df, *args, **kwargs):
            # Force ancestor_id column to have writable numpy backing
            phylogeny_df = phylogeny_df.copy()
            phylogeny_df["ancestor_id"] = phylogeny_df[
                "ancestor_id"
            ].to_numpy().copy()
            if "id" in phylogeny_df.columns:
                phylogeny_df["id"] = phylogeny_df["id"].to_numpy().copy()
            return _orig_reroot(phylogeny_df, *args, **kwargs)

        _rr.alifestd_reroot_at_id_asexual = _patched_reroot
        _rr._hstrat_patched = True
