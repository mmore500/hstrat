#!/usr/bin/env python3

import os
import random

import opytional as opyt

from hstrat import hstrat

try:
    from Bio import Phylo as BioPhylo
except (ImportError, ModuleNotFoundError) as e:
    print("biopython required for tree reconstruction example")
    print("python3 -m pip install biopython")
    raise e

assets_path = os.path.join(os.path.dirname(__file__), "assets")

if __name__ == "__main__":
    print("loaded template phylogeny from assets/example.newick:")
    template_tree = BioPhylo.read(f"{assets_path}/example.newick", "newick")
    template_tree.rooted = True
    BioPhylo.draw_ascii(template_tree)
    for clade in template_tree.find_clades():
        clade.branch_length = int(opyt.or_value(clade.branch_length, 0))

    print("simulated hstrat column inheritance along template phylogeny:")
    extant_population = hstrat.descend_template_phylogeny_biopython(
        template_tree,
        seed_column=hstrat.HereditaryStratigraphicColumn(
            hstrat.recency_proportional_resolution_algo.Policy(5)
        ),
    )

    depth_lookup = template_tree.depths()
    clade_lookup = {v: k for k, v in depth_lookup.items()}
    for column in extant_population:
        generation = column.GetNumStrataDeposited() - 1
        clade = clade_lookup[generation]
        print(clade.name, f"{generation} generations ==>", column)

    print()
    print("a few pairwise comparisons via hstrat columns")
    for _rep in range(8):
        c1, c2 = random.sample(extant_population, 2)
        print(
            "hstrat.calc_rank_of_mrca_bounds_between "
            f"{clade_lookup[c1.GetNumStrataDeposited() - 1].name} & {clade_lookup[c2.GetNumStrataDeposited() - 1].name}: "
            f"{hstrat.calc_rank_of_mrca_bounds_between(c1, c2, prior='arbitrary')}"
        )
