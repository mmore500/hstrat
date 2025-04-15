#!/usr/bin/env python3

import argparse
import functools
import gc
import os
import random
import sys
import types
import typing
import uuid

import downstream
from downstream import dstream
import numpy as np
import opytional as opyt
import pandas as pd
from tqdm import tqdm

from hstrat._auxiliary_lib import RngStateContext

try:
    from phylotrackpy import systematics
except (ImportError, ModuleNotFoundError) as e:
    print("phylotrackpy required for dstream surf evolution example")
    print("python3 -m pip install phylotrackpy")
    raise e

evolution_selector = random.Random(1)  # ensure consistent true phylogeny


def consistent_state_randrange(bitwidth: int):
    """A wrapper for randrange that preserves state regardless of bitwidth

    Motivation: the random state after randrange(2**64) was different
    than that of randrange(2**8), and we wanted to keep things like
    extracted fossils and generated UUIDs consistent between runs
    regardless of parameters like `differentia_bitwidth`. Therefore,
    we use this to avoid random state changing differently across runs.
    """
    return random.randrange(2**64) & ((1 << bitwidth) - 1)


def make_uuid4_fast(
    random_generator: typing.Union[types.ModuleType, random.Random]
) -> str:
    """Fast UUID4 generator, using lower-quality randomness."""
    return str(
        uuid.UUID(
            int=random_generator.getrandbits(128),
            version=4,
        )
    )


def extract_fossils(
    pop: typing.List,
    fossil_sample_proportion: float = 0.1,
) -> typing.List:
    """
    We extract CreateOffspring() instead of the parent itself, becauase
    parents with surviving children are not treated as leaf nodes by
    phylotrackpy; this simplifies true/reconst phylo comparison
    """
    return [
        parent.CreateOffspring(fossil=True)
        for parent in random.sample(
            pop,
            k=int(len(pop) * fossil_sample_proportion),
        )
    ]


def evolve_drift(
    population: typing.List,
    fossil_interval: typing.Optional[int] = None,
) -> typing.List:
    """
    Simple asexual evolutionary algorithm under drift conditions.
    Fossils refer to organisms saved in the middle of the process
    of evolution, when normally they would have been deleted for
    the next generation. Fossils supplement the final population
    to add a sampling of historical, extinct taxa as phylogeny tips.
    """
    # synchronous generations
    fossils = []
    for generation in tqdm(range(500)):
        population = [
            parent.CreateOffspring()
            for parent in evolution_selector.choices(
                population, k=len(population)
            )
        ]
        if fossil_interval and generation % fossil_interval == 0:
            with RngStateContext(random.randint(1, sys.maxsize)):
                fossils.extend(extract_fossils(population))

    # asyncrhonous generations
    nsplit = len(population) // 2
    for generation in tqdm(range(500)):
        population[:nsplit] = [
            parent.CreateOffspring()
            for parent in evolution_selector.choices(
                population[:nsplit], k=nsplit
            )
        ]
        if fossil_interval and generation % fossil_interval == 0:
            with RngStateContext(random.randint(1, sys.maxsize)):
                fossils.extend(extract_fossils(population))
        evolution_selector.shuffle(population)

    return [*fossils, *population]


def make_Organism(
    dstream_algo: types.ModuleType,
    differentia_bitwidth: int,
    surface_size: int,
    syst: systematics.Systematics,
) -> typing.Type:
    """
    Factory function to configure Organism class using `differentia_bitwidth`
    and `surface_size`, with `syst` to track phylogenies.
    """

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
            "dstream_T",
            "hstrat_surface",
            "is_fossil",
        ]

        # primary simulation business --- arbitrary data in this simple example
        trait: float

        # instrumentation: perfect tracking with phylotrackpy
        uid: str
        taxon: systematics.Taxon

        # instrumentation: approximate tracking with hstrat surface
        dstream_T: int
        hstrat_surface: np.ndarray

        # keep track of whether or not this Organism is a fossil
        is_fossil: bool

        @staticmethod
        def create_founder() -> "Organism":
            """Create a founder organism, with hstrat surface initailized."""
            founder = None
            with RngStateContext(random.randint(1, sys.maxsize)):
                for T in range(surface_size):
                    founder = opyt.apply_if_or_else(
                        founder,
                        lambda x: x.CreateOffspring(fossil=True),
                        Organism,
                    )
            assert founder.dstream_T == surface_size
            return founder

        def __init__(
            self: "Organism",
            parent_taxon: typing.Optional[systematics.Taxon] = None,
            parent_hstrat_surface: np.ndarray = empty_surface,
            parent_dstream_T: int = 0,
            trait: float = 0.0,
            is_fossil: bool = False,
        ) -> None:
            """Initialize organism, by default as root organism."""
            # handle primary simulation business...
            self.trait = (
                trait  # arbitrary example data, not used in simulation
            )

            # handle phylotrackpy instrumentation...
            self.uid = make_uuid4_fast(
                random if is_fossil else evolution_selector
            )
            self.taxon = syst.add_org(self, parent_taxon)

            # handle hstrat surface instrumentation...
            self.hstrat_surface = parent_hstrat_surface.copy()
            # ... deposit stratum...
            # hack to avoid varying ranges give different random states
            differentia_value = consistent_state_randrange(
                bitwidth=differentia_bitwidth
            )
            self.DepositStratum(differentia_value, parent_dstream_T)
            self.dstream_T = parent_dstream_T + 1
            self.is_fossil = is_fossil

        def __del__(self: "Organism") -> None:
            """Remove organism from phylotrackpy systematics."""
            syst.remove_org(self.taxon)

        def CreateOffspring(
            self: "Organism", *, fossil: bool = False
        ) -> "Organism":
            """Create an offspring organism, with mutation and
            generation-updated instrumentation."""
            return Organism(
                parent_taxon=self.taxon,
                parent_hstrat_surface=self.hstrat_surface.copy(),
                parent_dstream_T=self.dstream_T,
                trait=self.trait + np.random.uniform(-1, 1),
                is_fossil=fossil,
            )

        def DepositStratum(
            self: "Organism",
            differentia_value: int,
            dstream_T: int,
        ) -> None:
            assert dstream_algo.has_ingest_capacity(
                surface_size, dstream_T + 1
            )

            dstream_site = assign_site(surface_size, dstream_T)
            if dstream_site is not None:  # handle skip/discard case
                self.hstrat_surface[dstream_site] = differentia_value

        def ToHex(self: "Organism") -> str:
            """Serialize the organism to a hex string, for genome output."""
            T_arr = np.asarray(self.dstream_T, dtype=np.uint32)
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
                "dstream_algo": f"dstream.{algo_name}",
                "dstream_storage_bitoffset": 32,
                "dstream_storage_bitwidth": surface_bitwidth,
                "dstream_T_bitoffset": 0,
                "dstream_T_bitwidth": 32,
                "dstream_S": surface_size,
                "trait": self.trait,
                "is_fossil": self.is_fossil,
            }

    return Organism


def make_validation_record(
    Organism: typing.Type,
    n_gen: int,
    differentia_override: typing.Callable,
    validator_exploded: str,
    validator_unpacked: str,
) -> dict:
    """
    Generate ephemeral validation data for quality assurance. This
    helps ensure data is being written and read in the proper format
    in case of different endianness or other scenarios.
    """
    organism = None
    with RngStateContext(random.randint(1, sys.maxsize)):
        for T in range(n_gen):
            organism = opyt.apply_if_or_else(
                organism,
                Organism.CreateOffspring,
                Organism,
            )
            organism.DepositStratum(differentia_override(T), T)

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
    parser.add_argument(
        "--fossil-interval",
        type=int,
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
    np.random.seed(2)  # ensure reproducibility
    random.seed(2)

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
    common_ancestor = Organism.create_founder()
    init_population = [common_ancestor.CreateOffspring() for _ in range(100)]
    sampled_genomes = evolve_drift(
        init_population, fossil_interval=args.fossil_interval
    )

    # mark non-tip taxa extinct
    del common_ancestor
    del init_population
    gc.collect()

    print("num organisms retained in exact tracker:", syst.get_total_orgs())
    print("final population size:", len(sampled_genomes))

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
        *map(Organism.ToRecord, sampled_genomes),  # experiment data
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
