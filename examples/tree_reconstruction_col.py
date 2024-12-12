#!/usr/bin/env python3

try:
    import random
    import typing

    import alifedata_phyloinformatics_convert as apc
    import opytional as opyt
    import pandas as pd

    from hstrat import _auxiliary_lib as hstrat_auxlib
    from hstrat import hstrat
except:
    print(
        """
        Missing dependencies!
        Run

        python3 -m pip install hstrat

        to install necessary dependencies.
        """
    )
    raise

# simple asexual evolutionary algorithm under drift conditions
# 100 synchronous generations with population size 10
def evolve_drift_synchronous(population: typing.List) -> typing.List:
    # synchronous generations
    for generation in range(100):
        parents = random.choices(population, k=len(population))
        population = [parent.CreateOffspring() for parent in parents]

    return population


# example genome
# bundles (arbitrary) functional genome content with hereditary stratigraph
# annotation
class SimpleAnnotatedGenome:

    content: float  # put functional genome content here
    annotation: hstrat.HereditaryStratigraphicColumn

    def __init__(
        self: "SimpleAnnotatedGenome",
        content_: typing.Optional[float] = None,
        annotation_: typing.Optional[
            hstrat.HereditaryStratigraphicColumn
        ] = None,
    ) -> None:
        # generate functional genome content randomly if not provided
        self.content = opyt.or_value(
            content_,
            random.uniform(0, 100),
        )
        # create new annotation if not provided
        self.annotation = opyt.or_value(
            annotation_,
            hstrat.HereditaryStratigraphicColumn(
                # specify which stratum retention policy to use...
                # this policy guarantees uncertainty no longer than 25% of
                # time elapsed since the true phylogenetic event
                hstrat.recency_proportional_resolution_algo.Policy(4),
                # how many bits for "fingerprints" (aka differentia)
                # generated & stored in each layer of column (uses 1 byte)
                stratum_differentia_bit_width=8,
            ),
        )

    def CreateOffspring(
        self: "SimpleAnnotatedGenome",
    ) -> "SimpleAnnotatedGenome":
        return SimpleAnnotatedGenome(
            # mutate functional genetic content
            self.content + random.uniform(0.0, 1.0) % 100.0,
            # tag offspring with an independent copy of the annotation, with a
            # new "fingerprint" layer appended
            self.annotation.CloneDescendant(),
        )


if __name__ == "__main__":

    # ensure reproducible results
    hstrat_auxlib.seed_random(2)

    # do the evolution
    print("evolving 100 generations...")
    population: typing.List[SimpleAnnotatedGenome]
    population = evolve_drift_synchronous(
        [SimpleAnnotatedGenome() for __ in range(10)]
    )

    # speciation event!
    # divide populations in two and evolve sub-populations separately
    print("speciation event! dividing population into two halves")
    print("evolving another 100 generations...")
    population = evolve_drift_synchronous(
        population[: len(population) // 2]
    ) + evolve_drift_synchronous(population[len(population) // 2 :])

    # evolution done
    print("evolution done!")
    # extract annotations from genomes
    extant_annotations = [genome.annotation for genome in population]

    # estimated_phylogeny is stored in alife data standards format
    # https://alife-data-standards.github.io/alife-data-standards/phylogeny.html
    estimated_phylogeny: pd.DataFrame
    estimated_phylogeny = hstrat.build_tree(
        extant_annotations,
        # the `build_tree` function tracks the current best-known general
        # purpose reconstruction algorithm
        # pin to the current version (e.g., "1.7.2") for long-term stability
        # or pin to hstrat.__version__ to track latest algorithm updates
        version_pin=hstrat.__version__,
    )
    # translate to dendropy (which provides lots of phylogenetics tools)
    # via alifedata phyloinformatics conversion tool
    dendropy_tree = apc.alife_dataframe_to_dendropy_tree(
        estimated_phylogeny,
        setup_edge_lengths=True,
    )

    # draw the reconstruction! (note detection of speciation event)
    print(dendropy_tree.as_ascii_plot(plot_metric="age"))
