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

hstrat enables phylogenetic inference on distributed digital evolution populations

- Free software: MIT license
- Documentation: <https://hstrat.readthedocs.io>

## Install

`python3 -m pip install hstrat`

## Usage

```python3
from hstrat import hstrat

print("creating founder1 and founder2, which share no ancestry...")
founder1 = hstrat.HereditaryStratigraphicColumn(
    # retain strata from every generation
    stratum_retention_policy=hstrat.fixed_resolution_algo.Policy(1)
)
founder2 = hstrat.HereditaryStratigraphicColumn(
    # retain strata from every third generation
    stratum_retention_policy=hstrat.fixed_resolution_algo.Policy(3),
)

print(
    "   do founder1 and founder2 share any common ancestor?",
    hstrat.does_have_any_common_ancestor(founder1, founder2)
) # -> False

print("creating descendant2a, 10 generations removed from founder2...")
descendant2a = founder2.Clone()
for __ in range(10): descendant2a.DepositStratum()

print(
    "   do founder2 and descendant2a share any common ancestor?",
    hstrat.does_have_any_common_ancestor(founder2, descendant2a)
) # -> True

print("creating descendant2b, 20 generations removed from descendant2a...")
descendant2b = descendant2a.Clone()
for __ in range(20): descendant2b.DepositStratum()

print("creating descendant2c, 5 generations removed from descendant2a...")
descendant2c = descendant2a.Clone()
for __ in range(5): descendant2c.DepositStratum()

# note MRCA estimate uncertainty, caused by sparse stratum retention policy
print(
    "   estimate descendant2b generations since MRCA with descendant2c?",
    hstrat.calc_ranks_since_mrca_bounds_with(
      descendant2b,
      descendant2c,
      prior="arbitrary",
    ),
) # -> (19, 22)
print(
    "   estimate descendant2c generations since MRCA with descendant2b?",
    hstrat.calc_ranks_since_mrca_bounds_with(
      descendant2c,
      descendant2b,
      prior="arbitrary",
    ),
) # -> (4, 7)
print(
    "   estimate generation of MRCA between descendant2b and descendant2c?",
    hstrat.calc_rank_of_mrca_bounds_between(
      descendant2b, descendant2c, prior="arbitrary"
    ),
) # -> (9, 12)
```

As shown in the example above, all library components can be accessed directly from the convenience flat namespace `hstrat.hstrat`.

See `examples/` for more usage examples, including

* incorporation of hstrat annotations into a custom genome class,
* automatic stratum retention policy parameterization,
* pairwise and population-level phylogenetic inference, and
* phylogenetic tree reconstruction.

## Citing

If `hstrat` software or hereditary stratigraphy methodology contributes to a scholarly work, please cite it according to references provided [here](https://hstrat.readthedocs.io/en/latest/citing.html).
We would love to list your project using `hstrat` in our documentation, see more [here](https://hstrat.readthedocs.io/en/latest/projects.html).

## Credits

This package was created with Cookiecutter and the `audreyr/cookiecutter-pypackage` project template.

## hcat

![hcat](docs/assets/hcat-banner.png)
