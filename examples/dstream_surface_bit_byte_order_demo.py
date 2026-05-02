#!/usr/bin/env python3
"""Round-trip reference: pack 1-bit differentiae into a `sticky_algo`
surface buffer with explicit byte/bit ordering, hex-serialize, then
deserialize via `downstream.dataframe.explode_lookup_packed` and check
that the bits land back in the slots we wrote.

`sticky_algo` retains the first S deposits and drops the rest, so the
slot/Tbar map is trivial: slot k <-> Tbar k. That makes it the cleanest
algorithm for pinning down byte/bit order assumptions: any mismatch
between what we wrote and what we read back is an ordering bug, not an
artifact of the retention policy.

Conventions exercised here (matches `examples/evolve_dstream_surf.py`):
  * `dstream_T` packed as big-endian uint32 at the start of `data_hex`.
  * Surface bits packed via `numpy.packbits` with default ("big")
    bitorder, so slot 0 is the MSB of the first byte.
"""

import numpy as np
import pandas as pd
import polars as pl

import downstream
from downstream import dataframe as dstream_dataframe
from downstream import dstream

ALGO = dstream.sticky_algo
ALGO_NAME = "dstream.sticky_algo"

# (expected hex for the surface buffer, surface size S in bits)
CASES = [
    ("ad", 1 * 8),
    ("be", 1 * 8),
    ("beef", 2 * 8),
    ("feed", 2 * 8),
    ("dac0ffee", 4 * 8),
    ("fadeface", 4 * 8),
    ("decafbeabad00bee", 8 * 8),
    ("c0ffeebabedecade", 8 * 8),
]


def hex_to_bits(hex_str: str, nbits: int) -> np.ndarray:
    """Big-endian, MSB-first bit decoding of `hex_str` to `nbits` bits."""
    nbytes = (nbits + 7) // 8
    raw = bytes.fromhex(hex_str.ljust(nbytes * 2, "0"))
    bits = np.unpackbits(np.frombuffer(raw, dtype=np.uint8), bitorder="big")
    return bits[:nbits].astype(np.uint8)


def deposit_bits_to_hex(bits: np.ndarray, S: int) -> tuple[str, int]:
    """Run `bits` through sticky_algo deposits and serialize the resulting
    surface to hex, mirroring `examples/evolve_dstream_surf.py`."""
    surface = np.zeros(S, dtype=np.uint8)
    n_deposits = 0
    for T, value in enumerate(bits):
        assert ALGO.has_ingest_capacity(S, T + 1)
        site = ALGO.assign_storage_site(S, T)
        if site is not None:  # sticky drops deposits past the first S
            surface[site] = value
        n_deposits += 1

    # pack surface bits big-endian (slot 0 -> MSB of first byte)
    surface_hex = np.packbits(surface, bitorder="big").tobytes().hex()
    # T as big-endian uint32 prefix
    T_hex = np.uint32(n_deposits).astype(">u4").tobytes().hex()
    return T_hex + surface_hex, n_deposits


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
        exploded.to_pandas()
        .sort_values("dstream_Tbar")
        .reset_index(drop=True)
    )


if __name__ == "__main__":
    for expected_hex, S in CASES:
        # --- forward leg: bits -> numpy buffer -> hex -----------------
        bits_in = hex_to_bits(expected_hex, S)
        data_hex, T = deposit_bits_to_hex(bits_in, S)

        surface_hex = data_hex[8:]  # strip the 4-byte T prefix
        assert surface_hex == expected_hex.lower(), (
            f"serialize mismatch: got {surface_hex} expected {expected_hex}"
        )

        # --- reverse leg: hex -> bits via explode_lookup_packed -------
        df = unpack_hex(data_hex, S)
        bits_out = df["dstream_value"].to_numpy().astype(np.uint8)

        # sticky: slot k <-> Tbar k, so order is preserved
        np.testing.assert_array_equal(bits_in, bits_out)
        assert (df["dstream_Tbar"].to_numpy() == np.arange(S)).all()

        bits_str = "".join(map(str, bits_out.tolist()))
        print(f"`0x{expected_hex.lower()}` (S={S})  ->  `{bits_str}`  ok")

    print("all round-trips ok")
