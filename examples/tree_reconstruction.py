#!/usr/bin/python3

import itertools as it
import random
import string
import typing

import numpy as np

from hstrat import hstrat

try:
    from Bio import Phylo
    from Bio.Phylo.TreeConstruction import (
        DistanceMatrix,
        DistanceTreeConstructor,
    )
except e:
    print("biopython required for tree reconstruction example")
    print("python3 -m pip install biopython")
    raise e

from _SimpleGenomeAnnotatedWithDenseRetention import (
    SimpleGenomeAnnotatedWithDenseRetention,
)

# see here for example of how to incorporate hstrat into a custom genome
from _SimpleGenomeAnnotatedWithSparseRetention import (
    SimpleGenomeAnnotatedWithSparseRetention,
)


def to_tril(matrix):
    return [row[:row_idx] + [0] for row_idx, row in enumerate(matrix.tolist())]


def evolve_drift_synchronous(GenomeType: typing.Type) -> typing.List:
    population = [GenomeType() for __ in range(25)]
    # synchronous generations
    for generation in range(100):
        parents = random.choices(population, k=len(population))
        population = [parent.CreateOffspring() for parent in parents]

    return population


if __name__ == "__main__":
    for genome_type in (
        SimpleGenomeAnnotatedWithDenseRetention,
        SimpleGenomeAnnotatedWithSparseRetention,
    ):
        print("genome type", genome_type.__name__)

        extant_population = evolve_drift_synchronous(genome_type)

        # NOTE: this tree reconstruction approach is naive and fragile...
        # a more sophisticated, robust reconstruction approach is currently
        # being developed and will be an upcoming library feature
        distance_matrix = np.array(
            [
                [
                    sum(
                        it.chain(
                            hstrat.calc_ranks_since_mrca_bounds_with(i, j),
                            hstrat.calc_ranks_since_mrca_bounds_with(j, i),
                        )
                    )
                    if i != j
                    else 0.0
                    for j in (g.annotation for g in extant_population)
                ]
                for i in (g.annotation for g in extant_population)
            ]
        )
        taxon_labels = [*string.ascii_lowercase[: len(extant_population)]]
        bio_dm = DistanceMatrix(
            taxon_labels,
            to_tril(distance_matrix),
        )
        tree = DistanceTreeConstructor().upgma(bio_dm)

        Phylo.draw_ascii(tree)
