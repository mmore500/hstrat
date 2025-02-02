import typing
from unittest import mock

import numpy as np
import tqdm

class Records:
    def __init__(self, init_size: int) -> None: ...
    def addRecord(
        self,
        data_id: int,
        id: int,
        ancestor_id: int,
        search_ancestor_id: int,
        search_first_child_id: int,
        search_prev_sibling_id: int,
        search_next_sibling_id: int,
        rank: int,
        differentia: int,
    ) -> None: ...
    def __len__(self) -> int: ...

placeholder_value: int

def collapse_unifurcations(
    records: Records, dropped_only: bool
) -> Records: ...
def copy_records_to_dict(records: Records) -> dict[str, np.ndarray]: ...
def extract_records_to_dict(records: Records) -> dict[str, np.ndarray]: ...
def extend_tree_searchtable_cpp_from_exploded(
    records: Records,
    data_ids: np.ndarray,
    num_strata_depositeds: np.ndarray,
    ranks: np.ndarray,
    differentiae: np.ndarray,
    tqdm_progress_bar: typing.Union[typing.Type[tqdm.tqdm], mock.Mock],
) -> None: ...
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
