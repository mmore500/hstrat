#!/usr/bin/env python3

import argparse
import functools
import gc
import os
import random
import types
import typing
import uuid

import downstream
from downstream import dstream
import numpy as np
import opytional as opyt
import pandas as pd
from tqdm import tqdm

try:
    from phylotrackpy import systematics
except (ImportError, ModuleNotFoundError) as e:
    print("phylotrackpy required for dstream surf evolution example")
    print("python3 -m pip install phylotrackpy")
    raise e


def make_uuid4_fast() -> str:
    """Fast UUID4 generator, using lower-quality randomness."""
    return str(uuid.UUID(int=random.getrandbits(128), version=4))


def evolve_drift(population: typing.List) -> typing.List:
    """Simple asexual evolutionary algorithm under drift conditions."""
    selector = random.Random(1)  # ensure consistent true phylogeny

    # synchronous generations
    for generation in tqdm(range(500)):
        population = [
            parent.CreateOffspring()
            for parent in selector.choices(population, k=len(population))
        ]

    # asyncrhonous generations
    nsplit = len(population) // 2
    for generation in tqdm(range(500)):
        population[:nsplit] = [
            parent.CreateOffspring()
            for parent in selector.choices(population[:nsplit], k=nsplit)
        ]
        selector.shuffle(population)

    return population


def make_Organism(
    dstream_algo: types.ModuleType,
    differentia_bitwidth: int,
    surface_size: int,
    syst: systematics.Systematics,
) -> typing.Type:
    """Factory function to configure Organism class."""

    surf_dtype = {
        1: np.uint8,
        8: np.uint8,
        64: np.uint64,
    }[differentia_bitwidth]
    empty_surface = np.empty(surface_size, dtype=surf_dtype)
    empty_surface.setflags(write=False)

    surface_bitwidth = differentia_bitwidth * surface_size

    assign_site = functools.lru_cache(dstream_algo.assign_storage_site)
    algo_name = dstream_algo.__name__.split(".")[-1]

    class Organism:
        """Simple organism class, with instrumentation for both phylotrackpy
        and hstrat surface phylogeny tracking."""

        __slots__ = [
            "trait",
            "uid",
            "taxon",
            "generation_count",
            "hstrat_surface",
        ]

        # primary simulation business --- arbitrary data in this simple example
        trait: float

        # instrumentation: perfect tracking with phylotrackpy
        uid: str
        taxon: systematics.Taxon

        # instrumentation: approximate tracking with hstrat surface
        generation_count: int
        hstrat_surface: np.ndarray

        def __init__(
            self: "Organism",
            parent_taxon: typing.Optional[systematics.Taxon] = None,
            parent_hstrat_surface: np.ndarray = empty_surface,
            generation_count: int = 0,
            trait: float = 0.0,
        ) -> None:
            """Initialize organism, by default as root organism."""
            # handle primary simulation business...
            self.trait = (
                trait  # arbitrary example data, not used in simulation
            )

            # handle phylotrackpy instrumentation...
            self.uid = make_uuid4_fast()
            self.taxon = syst.add_org(self, parent_taxon)

            # handle hstrat surface instrumentation...
            self.generation_count = generation_count
            self.hstrat_surface = parent_hstrat_surface.copy()
            # ... deposit stratum...
            differentia_value = random.randrange(2**differentia_bitwidth)
            self.DepositStratum(differentia_value)

        def __del__(self: "Organism") -> None:
            """Remove organism from phylotrackpy systematics."""
            syst.remove_org(self.taxon)

        def CreateOffspring(self: "Organism") -> "Organism":
            """Create an offspring organism, with mutation and
            generation-updated instrumentation."""
            return Organism(
                parent_taxon=self.taxon,
                parent_hstrat_surface=self.hstrat_surface.copy(),
                generation_count=self.generation_count + 1,
                trait=self.trait + np.random.uniform(-1, 1),
            )

        def DepositStratum(self: "Organism", differentia_value: int) -> None:
            assert dstream_algo.has_ingest_capacity(
                surface_size, self.generation_count + 1
            )

            dstream_site = assign_site(surface_size, self.generation_count)
            if dstream_site is not None:  # handle skip/discard case
                self.hstrat_surface[dstream_site] = differentia_value

        def ToHex(self: "Organism") -> str:
            """Serialize the organism to a hex string, for genome output."""
            T_arr = np.asarray(self.generation_count + 1, dtype=np.uint32)
            T_bytes = T_arr.astype(">u4").tobytes()  # big-endian u32
            T_hex = T_bytes.hex()

            differentia_bytewidth = differentia_bitwidth // 8
            pack_op = [
                lambda x: x.astype(f">u{differentia_bytewidth}"),  # big-endian
                np.packbits,  # default big bitorder
            ][differentia_bitwidth == 1]
            surface_bits = pack_op(self.hstrat_surface)
            surface_bytes = surface_bits.tobytes()
            surface_hex = surface_bytes.hex()

            trait_arr = np.asarray(self.trait, dtype=np.float32)
            trait_bytes = trait_arr.tobytes()
            trait_hex = trait_bytes.hex()

            return T_hex + surface_hex + trait_hex

        def ToRecord(self: "Organism") -> dict:
            """Serialize the organism to a dictionary."""
            return {
                "downstream_version": downstream.__version__,
                "data_hex": self.ToHex(),
                "taxon_label": self.uid,
                "generation_count": self.generation_count,
                "dstream_algo": f"dstream.{algo_name}",
                "dstream_storage_bitoffset": 32,
                "dstream_storage_bitwidth": surface_bitwidth,
                "dstream_T_bitoffset": 0,
                "dstream_T_bitwidth": 32,
                "dstream_S": surface_size,
                "trait": self.trait,
            }

    return Organism


def make_validation_record(
    Organism: typing.Type,
    n_gen: int,
    differentia_override: typing.Callable,
    validator_exploded: str,
    validator_unpacked: str,
) -> dict:
    """Generate ephemeral validation data for quality assurance."""
    organism = None
    for T in range(n_gen):
        organism = opyt.apply_if_or_else(
            organism,
            Organism.CreateOffspring,
            Organism,
        )
        organism.DepositStratum(differentia_override(T))

    return {
        **organism.ToRecord(),
        "downstream_exclude_exploded": True,
        "downstream_validate_exploded": validator_exploded,
        "downstream_validate_unpacked": validator_unpacked,
    }


def _parse_args() -> argparse.Namespace:
    """Helper function to parse command line arguments."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--differentia-bitwidth", type=int, default=1)
    parser.add_argument("--surface-size", type=int, default=64)
    parser.add_argument(
        "--genome-df-path",
        type=str,
        default="/tmp/genome-evolve_surf_dstream.pqt",
    )
    parser.add_argument(
        "--phylo-df-path",
        type=str,
        default="/tmp/phylo-evolve_surf_dstream.csv",
    )

    args = parser.parse_args()

    if args.differentia_bitwidth not in (1, 8, 64):
        raise NotImplementedError()

    if args.surface_size < 8:
        raise NotImplementedError()

    if not args.phylo_df_path.endswith(".csv"):
        raise ValueError("phylo_df_path must end with '.csv'")

    return args


def _get_df_save_handler(path: str) -> typing.Callable:
    """Helper function to get the appropriate pandas dataframe save handler."""
    df_save_handlers = {
        ".csv": pd.DataFrame.to_csv,
        ".json": pd.DataFrame.to_json,
        ".pqt": pd.DataFrame.to_parquet,
        ".parquet": pd.DataFrame.to_parquet,
    }
    ext = os.path.splitext(path)[-1]
    try:
        return df_save_handlers[ext]
    except KeyError:
        raise ValueError(f"Unsupported dataframe path extension: {ext}")


if __name__ == "__main__":
    np.random.seed(1)  # ensure reproducibility
    random.seed(1)

    args = _parse_args()

    # configure organism class
    syst = systematics.Systematics(lambda x: x.uid)  # each org is own taxon
    syst.add_snapshot_fun(systematics.Taxon.get_info, "taxon_label")
    Organism = make_Organism(
        dstream_algo=dstream.steady_algo,
        differentia_bitwidth=args.differentia_bitwidth,
        surface_size=args.surface_size,
        syst=syst,
    )

    # do simulation
    common_ancestor = Organism()
    init_population = [common_ancestor.CreateOffspring() for _ in range(100)]
    end_population = evolve_drift(init_population)

    # mark non-tip taxa extinct
    del common_ancestor
    del init_population
    gc.collect()

    # set up validators to test during downstream processing
    S = args.surface_size
    checkerboard_validator = (
        "pl.col('dstream_value') == pl.col('dstream_Tbar') % 2"
    )
    block_validator = (
        f"pl.col('dstream_value') == pl.col('dstream_Tbar') // {S // 2 + 1}"
    )

    # write out the final population, including hstrat surface data
    genome_records = [
        *map(Organism.ToRecord, end_population),  # experiment data
        make_validation_record(  # ephemeral validation data
            Organism=Organism,
            n_gen=S,
            differentia_override=lambda T: T % 2,
            validator_exploded=checkerboard_validator,
            validator_unpacked=f"pl.col('dstream_T') == {S}",
        ),
        make_validation_record(  # ephemeral validation data
            Organism=Organism,
            n_gen=S + 1,
            differentia_override=lambda T: T % 2,
            validator_exploded=checkerboard_validator,
            validator_unpacked=f"pl.col('dstream_T') == {S + 1}",
        ),
        make_validation_record(  # ephemeral validation data
            Organism=Organism,
            n_gen=S,
            differentia_override=lambda T: T // (S // 2 + 1),
            validator_exploded=block_validator,
            validator_unpacked=f"pl.col('dstream_T') == {S}",
        ),
        make_validation_record(  # ephemeral validation data
            Organism=Organism,
            n_gen=S + 1,
            differentia_override=lambda T: T // (S // 2 + 1),
            validator_exploded=block_validator,
            validator_unpacked=f"pl.col('dstream_T') == {S + 1}",
        ),
    ]
    genome_df = pd.DataFrame(genome_records)
    _get_df_save_handler(args.genome_df_path)(genome_df, args.genome_df_path)

    # write out ground truth phylogeny
    syst.snapshot(args.phylo_df_path)
