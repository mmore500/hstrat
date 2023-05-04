import contexttimer as ctt
import more_itertools as mit
import pytest

from hstrat import hstrat
from hstrat._auxiliary_lib import is_base64


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
def test_pack_differentiae(differentia_bit_width, num_strata):
    original_strata = [
        hstrat.HereditaryStratum(
            differentia_bit_width=differentia_bit_width,
            deposition_rank=i,
        )
        for i in range(num_strata)
    ]
    packed_differentiae = hstrat.pack_differentiae(
        original_strata,
        differentia_bit_width,
    )
    assert is_base64(packed_differentiae)

    unpacked_differentiae = hstrat.unpack_differentiae(
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
def test_benchmark(differentia_bit_width):
    num_strata = 10000
    original_strata = [
        hstrat.HereditaryStratum(
            differentia_bit_width=differentia_bit_width,
            deposition_rank=i,
        )
        for i in range(num_strata)
    ]

    packed_differentiae = hstrat.pack_differentiae(
        original_strata,
        differentia_bit_width,
    )

    with ctt.Timer(factor=1000) as timer:
        hstrat.unpack_differentiae(
            packed_differentiae,
            differentia_bit_width,
        )

    print()
    print(
        f"differentia_bit_width={differentia_bit_width}",
        f"num_strata={num_strata}",
        f"timer.elapsed={timer.elapsed}",
    )
