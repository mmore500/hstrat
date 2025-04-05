![hstrat wordmark](docs/assets/hstrat-wordmark.png)

[
![PyPi](https://img.shields.io/pypi/v/hstrat.svg)
](https://pypi.python.org/pypi/hstrat)
[
![codecov](https://codecov.io/gh/mmore500/hstrat/branch/master/graph/badge.svg?token=JwMfFOpBBD)
](https://codecov.io/gh/mmore500/hstrat)
[
![Codacy Badge](https://app.codacy.com/project/badge/Grade/9ab14d415aa9458d97b4cf760b95f874)
](https://www.codacy.com/gh/mmore500/hstrat/dashboard)
[
![CI](https://github.com/mmore500/hstrat/actions/workflows/ci.yaml/badge.svg)
](https://github.com/mmore500/hstrat/actions)
[
![Read The Docs](https://readthedocs.org/projects/hstrat/badge/?version=latest)
](https://hstrat.readthedocs.io/en/latest/?badge=latest)
[
![GitHub stars](https://img.shields.io/github/stars/mmore500/hstrat.svg?style=round-square&logo=github&label=Stars&logoColor=white)](https://github.com/mmore500/hstrat)
[
![Zenodo](https://zenodo.org/badge/464531144.svg)
](https://zenodo.org/badge/latestdoi/464531144)
[![JOSS](https://joss.theoj.org/papers/10.21105/joss.04866/status.svg)](https://doi.org/10.21105/joss.04866)

_hstrat_ enables phylogenetic inference on distributed digital evolution populations

- Free software: MIT license
- Documentation: <https://hstrat.readthedocs.io>
- Repository: <https://github.com/mmore500/hstrat>

## Install

`python3 -m pip install hstrat`

A containerized release of `hstrat` is available via <ghcr.io>

```bash
singularity exec docker://ghcr.io/mmore500/hstrat:v1.19.0 python3 -m hstrat --help
```

## Features

_hstrat_ serves to enable **robust, efficient extraction of evolutionary history** from evolutionary simulations where centralized, direct phylogenetic tracking is not feasible.
Namely, in large-scale, **decentralized parallel/distributed evolutionary simulations**, where agents' evolutionary lineages migrate among many cooperating processors over the course of simulation.

_hstrat_ can

- accurately estimate **time since MRCA** among two or several digital agents, even for uneven branch lengths
- **reconstruct phylogenetic trees** for entire populations of evolving digital agents
- **serialize genome annotations** to/from text and binary formats
- provide **low-footprint** genome annotations (e.g., reasonably as low as **64 bits** each)
- be directly configured to satisfy **memory use limits** and/or **inference accuracy requirements**

_hstrat operates just as well in single-processor simulation, but direct phylogenetic tracking using a tool like [phylotrackpy](https://github.com/emilydolson/phylotrackpy/) should usually be preferred in such cases due to its capability for perfect record-keeping given centralized global simulation observability._

## Example Usage

This code briefly demonstrates,

1.  initialization of a population of `HereditaryStratigraphicColumn` of objects,
2.  generation-to-generation transmission of `HereditaryStratigraphicColumn` objects with simple synchronous turnover, and then
3.  reconstruction of phylogenetic history from the final population of `HereditaryStratigraphicColumn` objects.

```python3
from random import choice as rchoice
import alifedata_phyloinformatics_convert as apc
from hstrat import hstrat; print(f"{hstrat.__version__=}")  # when last ran?
from hstrat._auxiliary_lib import seed_random; seed_random(1)  # reproducibility

# initialize a small population of hstrat instrumentation
# (in full simulations, each column would be attached to an individual genome)
population = [hstrat.HereditaryStratigraphicColumn() for __ in range(5)]

# evolve population for 40 generations under drift
for _generation in range(40):
    population = [rchoice(population).CloneDescendant() for __ in population]

# reconstruct estimate of phylogenetic history
alifestd_df = hstrat.build_tree(population, version_pin=hstrat.__version__)
tree_ascii = apc.RosettaTree(alifestd_df).as_dendropy.as_ascii_plot(width=20)
print(tree_ascii)
```

```
hstrat.__version__='1.8.8'
              /--- 1
          /---+
       /--+   \--- 3
       |  |
   /---+  \------- 2
   |   |
+--+   \---------- 0
   |
   \-------------- 4
```

In [actual usage](https://hstrat.readthedocs.io/en/latest/demo-ping.html), each _hstrat_ column would be bundled with underlying genetic material of interest in the simulation --- entire genomes or, in systems with sexual recombination, individual genes.
The _hstrat_ columns are designed to operate as a neutral genetic annotation, enhancing observability of the simulation but not affecting its outcome.

## How it Works

In order to enable phylogenetic inference over fully-distributed evolutionary simulation, hereditary stratigraphy adopts a paradigm akin to phylogenetic work in natural history/biology.
In these fields, phylogenetic history is inferred through comparisons among genetic material of extant organisms, with --- in broad terms --- phylogenetic relatedness established through the extent of genetic similarity between organisms.
Phylogenetic tracking through _hstrat_, similarly, is achieved through analysis of similarity/dissimilarity among genetic material sampled over populations of interest.

Rather than random mutation as with natural genetic material, however, genetic material used by _hstrat_ is structured through _hereditary stratigraphy_.
This methodology, described fully in our documentation, provides strong guarantees on phylogenetic inferential power, minimizes memory footprint, and allows efficient reconstruction procedures.

See [here](https://hstrat.readthedocs.io/en/latest/mechanism.html) for more detail on underlying hereditary stratigraphy methodology.

## Getting Started

Refer to our documentation for a [quickstart guide](https://hstrat.readthedocs.io/en/latest/quickstart.html) and an [annotated end-to-end usage example](https://hstrat.readthedocs.io/en/latest/demo-ping.html).

The `examples/` folder provides extensive usage examples, including

- incorporation of hstrat annotations into a custom genome class,
- automatic stratum retention policy parameterization,
- pairwise and population-level phylogenetic inference, and
- phylogenetic tree reconstruction.

Interested users can find an explanation of how hereditary stratigraphy methodology implemented by _hstrat_ works "under the hood," information on project-specific _hstrat_ configuration, and full API listing for the _hstrat_ package in [the documentation](https://hstrat.readthedocs.io/).

## Citing

If _hstrat_ software or hereditary stratigraphy methodology contributes to a scholarly work, please cite it according to references provided [here](https://hstrat.readthedocs.io/en/latest/citing.html).
We would love to list your project using _hstrat_ in our documentation, see more [here](https://hstrat.readthedocs.io/en/latest/projects.html).

## Credits

This package was created with Cookiecutter and the `audreyr/cookiecutter-pypackage` project template.

## hcat

![hcat](docs/assets/hcat-banner.png)
