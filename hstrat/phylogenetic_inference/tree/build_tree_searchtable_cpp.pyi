import typing

import numpy as np
import tqdm

class Records:
    @property
    def dstream_data_id(self) -> memoryview: ...
    @property
    def id(self) -> memoryview: ...
    @property
    def ancestor_id(self) -> memoryview: ...
    @property
    def rank(self) -> memoryview: ...
    @property
    def differentia(self) -> memoryview: ...

def build_exploded(
    data_ids: np.ndarray,
    num_strata_depositeds: np.ndarray,
    ranks: np.ndarray,
    differentiae: np.ndarray,
    tqdm_progress_bar: typing.Optional[tqdm.tqdm] = None
) -> Records:
    ...

def build_normal(
    data_ids: typing.List[int],
    num_strata_depositeds: typing.List[int],
    ranks: typing.List[typing.List[int]],
    differentiae: typing.List[typing.List[int]],
    tqdm_progress_bar: typing.Optional[tqdm.tqdm] = None
) -> Records:
    ...
