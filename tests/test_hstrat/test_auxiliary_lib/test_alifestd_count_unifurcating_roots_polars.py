import polars as pl

from hstrat._auxiliary_lib import alifestd_count_unifurcating_roots_polars


def test_empty_df():
    df = pl.DataFrame(
        {"id": [], "ancestor_id": []},
        schema={"id": pl.Int64, "ancestor_id": pl.Int64},
    )
    assert alifestd_count_unifurcating_roots_polars(df) == 0


def test_singleton_root():
    df = pl.DataFrame(
        {
            "id": [0],
            "ancestor_id": [0],
        }
    )
    assert alifestd_count_unifurcating_roots_polars(df) == 0


def test_unifurcating_root():
    df = pl.DataFrame(
        {
            "id": [0, 1],
            "ancestor_id": [0, 0],
        }
    )
    assert alifestd_count_unifurcating_roots_polars(df) == 1


def test_bifurcating_root():
    df = pl.DataFrame(
        {
            "id": [0, 1, 2],
            "ancestor_id": [0, 0, 0],
        }
    )
    assert alifestd_count_unifurcating_roots_polars(df) == 0


def test_chain():
    df = pl.DataFrame(
        {
            "id": [0, 1, 2, 3, 4, 5, 6],
            "ancestor_id": [0, 0, 1, 2, 3, 4, 5],
        }
    )
    assert alifestd_count_unifurcating_roots_polars(df) == 1


def test_two_unifurcating_roots():
    df = pl.DataFrame(
        {
            "id": [0, 1, 2, 3, 4, 5, 6],
            "ancestor_id": [0, 0, 1, 2, 2, 5, 5],
        }
    )
    assert alifestd_count_unifurcating_roots_polars(df) == 2


def test_root_with_two_children():
    df = pl.DataFrame(
        {
            "id": [0, 1, 2, 3, 4, 5, 6],
            "ancestor_id": [0, 0, 1, 2, 3, 4, 0],
        }
    )
    assert alifestd_count_unifurcating_roots_polars(df) == 0


def test_strictly_bifurcating():
    df = pl.DataFrame(
        {
            "id": [0, 1, 2, 3, 4],
            "ancestor_id": [0, 0, 0, 1, 1],
        }
    )
    assert alifestd_count_unifurcating_roots_polars(df) == 0
