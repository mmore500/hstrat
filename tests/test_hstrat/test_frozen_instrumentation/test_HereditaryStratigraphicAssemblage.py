from iterpop import iterpop as ip
import numpy as np
import pandas as pd
import pytest

from hstrat import hstrat


def test_hsa_empty():
    hsa = hstrat.HereditaryStratigraphicAssemblage([])
    assert [*hsa.IterSpecimens()] == []


def test_hsa_singleton():
    spec1 = pd.Series(data=[0, 8], index=[0, 1], dtype="uint8")
    hsa = hstrat.HereditaryStratigraphicAssemblage([spec1])
    assert all(ip.popsingleton(hsa.IterSpecimens()) == spec1)
    assert ip.popsingleton(hsa.IterSpecimens()).dtype.name == "UInt8"


def test_hsa_pair1():
    spec1 = pd.Series(data=[42, 42], index=[0, 2], dtype="uint64")
    spec2 = pd.Series(data=[111111, 0, 94], index=[0, 2, 3], dtype="uint64")
    hsa = hstrat.HereditaryStratigraphicAssemblage([spec1, spec2])

    res1, res2 = hsa.IterSpecimens()

    assert res1.equals(
        pd.Series(data=[42, 42, pd.NA], index=[0, 2, 3], dtype="UInt64")
    )
    assert res2.equals(
        pd.Series(data=[111111, 0, 94], index=[0, 2, 3], dtype="UInt64")
    )


def test_hsa_pair2():
    spec1 = pd.Series(data=[42, 41, 42], index=[0, 1, 2], dtype="uint64")
    spec2 = pd.Series(data=[111111, 0, 94], index=[0, 2, 3], dtype="uint64")
    hsa = hstrat.HereditaryStratigraphicAssemblage([spec1, spec2])

    res1, res2 = hsa.IterSpecimens()

    assert res1.equals(
        pd.Series(data=[42, 41, 42, pd.NA], index=[0, 1, 2, 3], dtype="UInt64")
    )
    assert res2.equals(
        pd.Series(
            data=[111111, pd.NA, 0, 94], index=[0, 1, 2, 3], dtype="UInt64"
        )
    )
