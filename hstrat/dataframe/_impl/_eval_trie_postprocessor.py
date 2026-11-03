import typing

import numpy as np
import phyloframe as pf
import polars as pl
from tqdm import tqdm

from ... import hstrat


def eval_trie_postprocessor(source: str) -> typing.Callable:
    """Evaluate a trie postprocessor from CLI source code.

    Evaluated with `hstrat` (the flat `hstrat.hstrat` namespace), `np`
    (numpy), `pf` (phyloframe), `pl` (polars), and `tqdm` available.
    """
    namespace = {"hstrat": hstrat, "np": np, "pf": pf, "pl": pl, "tqdm": tqdm}
    return eval(source, namespace)  # nosec B307
