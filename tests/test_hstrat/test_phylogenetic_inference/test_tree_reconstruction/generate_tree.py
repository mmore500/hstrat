from hstrat import hstrat
import typing

from _SimpleGenomeAnnotatedWithDenseRetention import (
    SimpleGenomeAnnotatedWithDenseRetention,
)

def evolve_drift_synchronous(GenomeType: typing.Type) -> typing.List:
    population = [GenomeType() for __ in range(10)]
    # synchronous generations
    for generation in range(100):
        parents = random.choices(population, k=len(population))
        population = [parent.CreateOffspring() for parent in parents]

    return population

extant_population = evolve_drift_synchronous(SimpleGenomeAnnotatedWithDenseRetention)
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
    genome.annotation for genome in extant_population
)
print(
    "   population MRCA estmated between generation",
    mrca_lb,
    "and",
    mrca_ub,
)
