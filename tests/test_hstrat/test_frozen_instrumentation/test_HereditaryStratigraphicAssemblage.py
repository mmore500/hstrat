from iterpop import iterpop as ip
import pandas as pd

from hstrat import hstrat


def test_hsa_empty():
    hsa = hstrat.HereditaryStratigraphicAssemblage([])
    assert [*hsa.BuildSpecimens()] == []


def test_hsa_singleton():
    spec1 = hstrat.HereditaryStratigraphicSpecimen(
        pd.Series(data=[0, 8], index=[0, 1], dtype="uint8"), 8
    )
    hsa = hstrat.HereditaryStratigraphicAssemblage([spec1])
    assert all(
        ip.popsingleton(hsa.BuildSpecimens()).GetData() == spec1.GetData()
    )
    assert (
        ip.popsingleton(hsa.BuildSpecimens()).GetData().dtype.name == "UInt8"
    )
    assert (
        ip.popsingleton(hsa.BuildSpecimens()).GetStratumDifferentiaBitWidth()
        == spec1.GetStratumDifferentiaBitWidth()
    )
    assert 1 == len(
        set(
            specimen.GetStratumMask().shape
            for specimen in hsa.BuildSpecimens()
        )
    )
    assert 1 == len(
        set(
            specimen.GetDifferentiaVals().shape
            for specimen in hsa.BuildSpecimens()
        )
    )


def test_hsa_pair1():
    spec1 = hstrat.HereditaryStratigraphicSpecimen(
        pd.Series(data=[42, 42], index=[0, 2], dtype="uint64"), 64
    )
    spec2 = hstrat.HereditaryStratigraphicSpecimen(
        pd.Series(data=[111111, 0, 94], index=[0, 2, 3], dtype="uint64"), 64
    )
    hsa = hstrat.HereditaryStratigraphicAssemblage([spec1, spec2])
    assert 1 == len(
        set(
            specimen.GetStratumMask().shape
            for specimen in hsa.BuildSpecimens()
        )
    )
    assert 1 == len(
        set(
            specimen.GetDifferentiaVals().shape
            for specimen in hsa.BuildSpecimens()
        )
    )

    res1, res2 = hsa.BuildSpecimens()

    assert res1.GetData().equals(
        pd.Series(data=[42, 42, pd.NA], index=[0, 2, 3], dtype="UInt64")
    )
    assert (
        res1.GetStratumDifferentiaBitWidth()
        == spec1.GetStratumDifferentiaBitWidth()
    )
    assert res2.GetData().equals(
        pd.Series(data=[111111, 0, 94], index=[0, 2, 3], dtype="UInt64")
    )
    assert (
        res2.GetStratumDifferentiaBitWidth()
        == spec2.GetStratumDifferentiaBitWidth()
    )


def test_hsa_pair2():
    spec1 = hstrat.HereditaryStratigraphicSpecimen(
        pd.Series(data=[42, 41, 42], index=[0, 1, 2], dtype="uint64"), 64
    )
    spec2 = hstrat.HereditaryStratigraphicSpecimen(
        pd.Series(data=[111111, 0, 94], index=[0, 2, 3], dtype="uint64"), 64
    )
    hsa = hstrat.HereditaryStratigraphicAssemblage([spec1, spec2])
    assert 1 == len(
        set(
            specimen.GetStratumMask().shape
            for specimen in hsa.BuildSpecimens()
        )
    )
    assert 1 == len(
        set(
            specimen.GetDifferentiaVals().shape
            for specimen in hsa.BuildSpecimens()
        )
    )

    res1, res2 = hsa.BuildSpecimens()

    assert res1.GetData().equals(
        pd.Series(data=[42, 41, 42, pd.NA], index=[0, 1, 2, 3], dtype="UInt64")
    )
    assert (
        res1.GetStratumDifferentiaBitWidth()
        == spec1.GetStratumDifferentiaBitWidth()
    )
    assert res2.GetData().equals(
        pd.Series(
            data=[111111, pd.NA, 0, 94], index=[0, 1, 2, 3], dtype="UInt64"
        )
    )
    assert (
        res2.GetStratumDifferentiaBitWidth()
        == spec2.GetStratumDifferentiaBitWidth()
    )


def test_hsa_pair3():
    spec1 = hstrat.HereditaryStratigraphicSpecimen(
        pd.Series(data=[42, 41, 42], index=[0, 1, 2], dtype="uint64"), 64
    )
    spec2 = hstrat.HereditaryStratigraphicSpecimen(
        pd.Series(
            data=[111111, 0, 94, 78], index=[0, 2, 3, 4], dtype="uint64"
        ),
        64,
    )
    hsa = hstrat.HereditaryStratigraphicAssemblage([spec1, spec2])
    assert 1 == len(
        set(
            specimen.GetStratumMask().shape
            for specimen in hsa.BuildSpecimens()
        )
    )
    assert 1 == len(
        set(
            specimen.GetDifferentiaVals().shape
            for specimen in hsa.BuildSpecimens()
        )
    )

    res1, res2 = hsa.BuildSpecimens()

    assert res1.GetData().equals(
        pd.Series(
            data=[42, 41, 42, pd.NA, pd.NA],
            index=[0, 1, 2, 3, 4],
            dtype="UInt64",
        )
    )
    assert (
        res1.GetStratumDifferentiaBitWidth()
        == spec1.GetStratumDifferentiaBitWidth()
    )
    assert res2.GetData().equals(
        pd.Series(
            data=[111111, pd.NA, 0, 94, 78],
            index=[0, 1, 2, 3, 4],
            dtype="UInt64",
        )
    )
    assert (
        res2.GetStratumDifferentiaBitWidth()
        == spec2.GetStratumDifferentiaBitWidth()
    )
