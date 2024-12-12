#!/usr/bin/env python3

import random
import typing

from _SimpleGenomeAnnotatedWithDenseRetention import (
    SimpleGenomeAnnotatedWithDenseRetention,
)

# see here for example of how to incorporate hstrat into a custom genome
from _SimpleGenomeAnnotatedWithSparseRetention import (
    SimpleGenomeAnnotatedWithSparseRetention,
)

from hstrat import hstrat


def evolve_drift_synchronous(GenomeType: typing.Type) -> typing.List:
    population = [GenomeType() for __ in range(10)]
    # synchronous generations
    for generation in range(100):
        parents = random.choices(population, k=len(population))
        population = [parent.CreateOffspring() for parent in parents]

    return population


def evolve_tournament_synchronous(GenomeType: typing.Type) -> typing.List:
    population = [GenomeType() for __ in range(20)]

    # asynchronous generations
    for generation in range(100):
        # tournament selection with tournament size 7
        parents = [
            min(
                random.sample(population, k=7),
                key=lambda genome: genome.content,
            )
            for __ in population
        ]
        population = [parent.CreateOffspring() for parent in parents]

    return population


def evolve_tournament_asynchronous(GenomeType: typing.Type) -> typing.List:
    population = [GenomeType() for __ in range(20)]

    # asynchronous generations
    for generation in range(100 * 20):
        # tournament selection with tournament size 7
        random.shuffle(population)
        population[0] = min(
            random.sample(population, k=7),
            key=lambda genome: genome.content,
        ).CreateOffspring()

    return population


if __name__ == "__main__":
    for genome_type in (
        SimpleGenomeAnnotatedWithDenseRetention,
        SimpleGenomeAnnotatedWithSparseRetention,
    ):
        for experiment in (
            evolve_drift_synchronous,
            evolve_tournament_synchronous,
            evolve_tournament_asynchronous,
        ):
            print("genome type", genome_type.__name__)
            print("experiment", experiment.__name__)

            extant_population = experiment(genome_type)
            min_generations = min(
                genome.annotation.GetNumStrataDeposited()
                for genome in extant_population
            )
            print("   min generations elapsed", min_generations)
            max_generations = max(
                genome.annotation.GetNumStrataDeposited()
                for genome in extant_population
            )
            print("   max generations elapsed", max_generations)

            mrca_lb, mrca_ub = hstrat.calc_rank_of_mrca_bounds_among(
                (genome.annotation for genome in extant_population),
                prior="arbitrary",
            )
            print(
                "   population MRCA estmated between generation",
                mrca_lb,
                "and",
                mrca_ub,
            )

            print()
