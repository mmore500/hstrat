import more_itertools as mit
import pytest
import typing_extensions

from hstrat import hstrat


@pytest.mark.parametrize(
    "differentia_bit_width",
    [
        1,
        8,
        16,
        32,
        64,
    ],
)
@pytest.mark.parametrize(
    "num_strata",
    [
        0,
        1,
        2,
        7,
        8,
        15,
        27,
        32,
    ],
)
def test_pack_differentiae_bytes(differentia_bit_width, num_strata):
    original_strata = [
        hstrat.HereditaryStratum(
            differentia_bit_width=differentia_bit_width,
            deposition_rank=i,
        )
        for i in range(num_strata)
    ]
    packed_differentiae = hstrat.pack_differentiae_bytes(
        original_strata,
        differentia_bit_width,
    )
    assert isinstance(packed_differentiae, typing_extensions.Buffer)

    unpacked_differentiae = hstrat.unpack_differentiae_bytes(
        packed_differentiae,
        differentia_bit_width,
    )

    for stratum, differentia in mit.zip_equal(
        original_strata,
        unpacked_differentiae,
    ):
        assert stratum.GetDifferentia() == differentia


@pytest.mark.parametrize(
    "differentia_bit_width",
    [
        1,
        8,
        16,
        32,
        64,
    ],
)
@pytest.mark.parametrize(
    "num_strata",
    [
        0,
        1,
        2,
        7,
        8,
        15,
        27,
        32,
    ],
)
def test_pack_differentiae_bytes_specify_num_differentia_packed(
    differentia_bit_width, num_strata
):
    original_strata = [
        hstrat.HereditaryStratum(
            differentia_bit_width=differentia_bit_width,
            deposition_rank=i,
        )
        for i in range(num_strata)
    ]
    packed_differentiae = hstrat.pack_differentiae_bytes(
        original_strata,
        differentia_bit_width,
        always_omit_num_padding_bits_header=True,
    )
    assert isinstance(packed_differentiae, typing_extensions.Buffer)

    unpacked_differentiae = hstrat.unpack_differentiae_bytes(
        packed_differentiae,
        differentia_bit_width,
        num_packed_differentia=len(original_strata),
    )

    for stratum, differentia in mit.zip_equal(
        original_strata,
        unpacked_differentiae,
    ):
        assert stratum.GetDifferentia() == differentia
