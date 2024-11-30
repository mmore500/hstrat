import typing

import numpy as np
import tqdm

class RecordHolder_C:
    def collect_dstream_data_id(self) -> np.ndarray: ...
    def collect_id(self) -> np.ndarray: ...
    def collect_ancestor_id(self) -> np.ndarray: ...
    def collect_rank(self) -> np.ndarray: ...
    def collect_differentia(self) -> np.ndarray: ...

def build_exploded(
    data_ids: np.ndarray,
    num_strata_depositeds: np.ndarray,
    ranks: np.ndarray,
    differentiae: np.ndarray,
    tqdm_progress_bar: typing.Optional[typing.Type[tqdm.tqdm]] = None,
) -> RecordHolder_C: ...
def build_normal(
    data_ids: typing.List[int],
    num_strata_depositeds: typing.List[int],
    ranks: typing.List[typing.List[int]],
    differentiae: typing.List[typing.List[int]],
    tqdm_progress_bar: typing.Optional[typing.Type[tqdm.tqdm]] = None,
) -> RecordHolder_C: ...
