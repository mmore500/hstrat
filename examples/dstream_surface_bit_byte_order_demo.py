#!/usr/bin/env python3
"""
Bit/byte-order reference for dstream surface buffers.

Use this as a debug aid when you suspect a packing/unpacking mismatch:
each case pins down the exact bit string that lives behind a given hex
blob under the conventions used in `examples/evolve_dstream_surf.py`.

Conventions exercised here (matches `examples/evolve_dstream_surf.py`):
  * `dstream_T` packed as big-endian uint32 at the start of `data_hex`.
  * Surface bits packed via `numpy.packbits` with default ("big")
    bitorder, so slot 0 is the MSB of the first byte.

`sticky_algo` is used only as a convenient vehicle: it deposits the
first S values into slots 0..S-1 in order, so the (slot, Tbar) map is
the identity and any mismatch we see is unambiguously a byte/bit-order
bug rather than a retention-policy artifact.
"""

import downstream
from downstream import dataframe as dstream_dataframe
from downstream import dstream
import numpy as np
import pandas as pd
import polars as pl

ALGO = dstream.sticky_algo
ALGO_NAME = "dstream.sticky_algo"

# (surface hex, surface as base-10 int, surface as bit string)
# Each row is the same value written three ways under big-endian/
# MSB-first packing. S is derived as len(hex) * 4.
CASES = [
    ("ad", 173, "10101101"),
    ("be", 190, "10111110"),
    ("beef", 48879, "1011111011101111"),
    ("feed", 65261, "1111111011101101"),
    (
        "dac0ffee",
        3670081518,
        "11011010110000001111111111101110",
    ),
    (
        "fadeface",
        4208917198,
        "11111010110111101111101011001110",
    ),
    (
        "decafbeabad00bee",
        16053920807290670062,
        "1101111011001010111110111110101010111010110100000000101111101110",
    ),
    (
        "c0ffeebabedecade",
        13907096660176980702,
        "1100000011111111111011101011101010111110110111101100101011011110",
    ),
]


def hex_to_bits(hex_str: str) -> np.ndarray:
    """Big-endian, MSB-first bit decoding of `hex_str`."""
    raw = bytes.fromhex(hex_str)
    return np.unpackbits(np.frombuffer(raw, dtype=np.uint8), bitorder="big")


def deposit_bits_to_hex_array(bits: np.ndarray) -> str:
    """
    Pack via a length-S numpy uint8 array, one slot per element.

    Mirrors the byte/bit ordering used in
    `examples/evolve_dstream_surf.py`.
    """
    S = len(bits)
    surface = np.zeros(S, dtype=np.uint8)
    for T, value in enumerate(bits):
        assert ALGO.has_ingest_capacity(S, T + 1)
        site = ALGO.assign_storage_site(S, T)
        assert site is not None  # len(bits) == S, so no deposit is dropped
        surface[site] = value

    # pack surface bits big-endian (slot 0 -> MSB of first byte)
    surface_hex = np.packbits(surface, bitorder="big").tobytes().hex()
    # T as big-endian uint32 prefix
    T_hex = np.uint32(S).astype(">u4").tobytes().hex()
    return T_hex + surface_hex


def deposit_bits_to_hex_scalar(bits: np.ndarray) -> str:
    """
    Pack via bitwise ops on a single numpy scalar (uint8/16/32/64).

    Mirrors the scalar-buffer pattern used in
    https://github.com/mmore500/allele-evoepi-concept/blob/main/bindle/2026-04-29-allele-abm-phylogeny-hstrat-32site.py
    where slot k occupies bit `(S - 1) - k`, i.e. slot 0 is the MSB.
    """
    S = len(bits)
    # smallest unsigned dtype that holds an S-bit value
    dtype = np.min_scalar_type(2**S - 1).type
    surface = dtype(0)
    for T, value in enumerate(bits):
        assert ALGO.has_ingest_capacity(S, T + 1)
        site = ALGO.assign_storage_site(S, T)
        assert site is not None
        surface ^= dtype(value) << dtype(S - 1 - site)

    bytewidth = np.dtype(dtype).itemsize
    # gotcha: on numpy 2.x, scalar.astype(">uN") drops the byte-order
    # qualifier and emits native-endian bytes. wrapping in np.asarray
    # gives a 0-d array, which honors `>` correctly.
    surface_hex = np.asarray(surface).astype(f">u{bytewidth}").tobytes().hex()
    T_hex = np.uint32(S).astype(">u4").tobytes().hex()
    return T_hex + surface_hex


def unpack_hex(data_hex: str, S: int) -> pd.DataFrame:
    """Decode the (T_hex + surface_hex) blob via downstream's unpacker."""
    storage_bitwidth = ((S + 7) // 8) * 8
    df = pl.from_pandas(
        pd.DataFrame(
            [
                {
                    "downstream_version": downstream.__version__,
                    "data_hex": data_hex,
                    "dstream_algo": ALGO_NAME,
                    "dstream_storage_bitoffset": 32,
                    "dstream_storage_bitwidth": storage_bitwidth,
                    "dstream_T_bitoffset": 0,
                    "dstream_T_bitwidth": 32,
                    "dstream_S": S,
                },
            ],
        ),
    )
    exploded = dstream_dataframe.explode_lookup_packed(df, value_type="uint8")
    return (
        exploded.to_pandas().sort_values("dstream_Tbar").reset_index(drop=True)
    )


if __name__ == "__main__":
    for expected_hex, expected_int, expected_bits in CASES:
        S = len(expected_hex) * 4
        assert len(expected_bits) == S

        # parallel cross-checks: hex, 0b... int, and bit string must
        # all describe the same value under big-endian/MSB-first packing
        assert int(expected_hex, 16) == expected_int
        assert format(expected_int, f"0{S}b") == expected_bits
        bits_in = np.array([int(c) for c in expected_bits], dtype=np.uint8)
        np.testing.assert_array_equal(bits_in, hex_to_bits(expected_hex))

        # --- forward leg: bits -> numpy buffer -> hex -----------------
        # both buffer styles (length-S uint8 array, single scalar) must
        # serialize to the same hex blob
        data_hex = deposit_bits_to_hex_array(bits_in)
        assert data_hex == deposit_bits_to_hex_scalar(bits_in)
        surface_hex = data_hex[8:]  # strip the 4-byte T prefix
        assert surface_hex == expected_hex.lower()

        # --- reverse leg: hex -> bits via explode_lookup_packed -------
        df = unpack_hex(data_hex, S)
        bits_out = df["dstream_value"].to_numpy().astype(np.uint8)

        # sticky: slot k <-> Tbar k, so order is preserved
        np.testing.assert_array_equal(bits_in, bits_out)
        assert (df["dstream_Tbar"].to_numpy() == np.arange(S)).all()

        print(f"`0x{expected_hex.lower()}` (S={S})  ->  `{expected_bits}`  ok")

    print("all round-trips ok")
