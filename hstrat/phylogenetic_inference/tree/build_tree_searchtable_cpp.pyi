import typing

import numpy as np
import tqdm

class Records:
    dstream_data_id: memoryview
    id: memoryview
    ancestor_id: memoryview
    rank: memoryview
    differentia: memoryview

def build(
    data_ids: np.ndarray,
    num_strata_depositeds: np.ndarray,
    ranks: np.ndarray,
    differentiae: np.ndarray,
    tqdm_progress_bar: typing.Optional[tqdm.tqdm],
) -> Records:
    pass
