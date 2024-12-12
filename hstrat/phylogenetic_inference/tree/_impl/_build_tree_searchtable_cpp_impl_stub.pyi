import typing
from unittest import mock

import numpy as np
import tqdm

def build_tree_searchtable_cpp_from_exploded(
    data_ids: np.ndarray,
    num_strata_depositeds: np.ndarray,
    ranks: np.ndarray,
    differentiae: np.ndarray,
    tqdm_progress_bar: typing.Union[typing.Type[tqdm.tqdm], mock.Mock],
) -> dict[str, np.ndarray]: ...
def build_tree_searchtable_cpp_from_nested(
    data_ids: typing.List[int],
    num_strata_depositeds: typing.List[int],
    ranks: typing.List[typing.List[int]],
    differentiae: typing.List[typing.List[int]],
    tqdm_progress_bar: typing.Union[typing.Type[tqdm.tqdm], mock.Mock],
) -> dict[str, np.ndarray]: ...
