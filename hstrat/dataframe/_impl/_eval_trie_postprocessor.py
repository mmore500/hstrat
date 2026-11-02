import typing

import numpy as np
import phyloframe as pf
import polars as pl


def eval_trie_postprocessor(source: str) -> typing.Callable:
    """Evaluate a trie postprocessor from CLI source code.

    Evaluated with `hstrat` (the flat `hstrat.hstrat` namespace), `np`
    (numpy), `pf` (phyloframe), and `pl` (polars) available.
    """
    from ... import hstrat

    namespace = {"hstrat": hstrat, "np": np, "pf": pf, "pl": pl}
    return eval(source, namespace)  # nosec B307
