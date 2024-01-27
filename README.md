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

## Available Stratum Retention Algorithms

The space-vs-resolution and distribution-of-resolution trade-offs of library-provided stratum retention algorithms are summarized below.

| Stratum Retention Algorithm               | Space Complexity | MRCA Gen Uncertainty |
| ----------------------------------------- | ---------------- | -------------------- |
| Fixed Resolution Algorithm                | `n/k`            | `k`                  |
| Recency-proportional Resolution Algorithm | `k * log(n)`     | `m/k`                |
| Depth-proportional Resolution Algorithm   | `k`              | `n/k`                |
| Geometric Sequence Nth Root Algorithm     | `k`              | `m * n^(1/k)`        |
| Curbed Recency-proportional Resolution Algorithm | `k`     | `m / k` -> `m * n^(1/k)` |

where `n` is generations elapsed, `m` is generations since MRCA, and `k` is an arbitrary user-determined constant.

Note that distribution-of-resolution trade-offs are described via the definition of uncertainty bounds in terms of generations since MRCA `m` versus overall generations elapsed `n`.

The `hstrat` library includes a suite of variants for several of these stratum retention algorithms.
These variants differ in terms of secondary considerations, for example whether column size exactly traces the asymptotic guarantee or fluctuates around it.
Computational intensity to calculate the set of strata to be dropped at each generation may also differ between variants.

The next sections tour available stratum retention algorithms in detail.

### Retention Drip Plot Visualization

| No History                                                                                                                                                                                                                                                                                                                                                                                                                                                         | Retained History                                                                                                                                                                                                                                                                                                                                                                                                                                                  | All History                                                                                                                                                                                                                                                                                                                                                                                                                                                       |
| ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [![](docs/assets/a=stratum_retention_dripplot+extant_history=False+extinct_history=False+extinct_placeholders=True+num_generations=256+policy=tapered-depth-proportional-resolution-stratum-retention-algorithm-resolution-4+ext=.gif)](docs/assets/a=stratum_retention_dripplot+extant_history=False+extinct_history=False+extinct_placeholders=True+num_generations=256+policy=tapered-depth-proportional-resolution-stratum-retention-algorithm-resolution-4+ext=.gif) | [![](docs/assets/a=stratum_retention_dripplot+extant_history=True+extinct_history=False+extinct_placeholders=True+num_generations=256+policy=tapered-depth-proportional-resolution-stratum-retention-algorithm-resolution-4+ext=.gif)](docs/assets/a=stratum_retention_dripplot+extant_history=True+extinct_history=False+extinct_placeholders=True+num_generations=256+policy=tapered-depth-proportional-resolution-stratum-retention-algorithm-resolution-4+ext=.gif) | [![](docs/assets/a=stratum_retention_dripplot+extant_history=True+extinct_history=True+extinct_placeholders=False+num_generations=256+policy=tapered-depth-proportional-resolution-stratum-retention-algorithm-resolution-4+ext=.gif)](docs/assets/a=stratum_retention_dripplot+extant_history=True+extinct_history=True+extinct_placeholders=False+num_generations=256+policy=tapered-depth-proportional-resolution-stratum-retention-algorithm-resolution-4+ext=.gif) |

Because stratum retention policies unfold across space and time (i.e., the location of pruned strata and the generations at which they are pruned), the retention drip plot visualizations we use to depict them require a bit of explanation to get up to speed with.
This section builds up the visualizations step-by-step in the table above.
(Note that the animations loop at 256 generations; if you are impatient you can refresh the page to restart the animations.)

The leftmost column animates the evolution of a single hereditary stratigraphic column over generations with no historical overlay.
The column itself is shown "tipped over," appearing as a horizontal blue rectangle.
Upside-down triangles are stratum within the column.
The position of strata in the `x` dimension correspond to the generation of their deposition; new strata are appended on the right.
Retention status is depicted with color.
Black strata are retained and red strata have been pruned.

The center column uses the `y` dimension to introduce historical traces for retained strata.
The line below each retained stratum spans from the generation it was deposited to the current generation.
Note that the column itself is positioned at the current generation at the top of the diagram.

Finally, the rightmost column further layers on historical traces of pruned strata.
Instead of having their trace deleted when pruned, their trace is turned red and frozen in place.
So, red traces span from the generation a pruned stratum was deposited to the generation it was pruned.

Animated panels below situate this visualization alongside additional graphs depicting absolute and relative estimation error across possible MRCA generations as well as relative and absolute column size (i.e., number of strata retained).
Two policy instantiations are visualized for each algorithm --- one yielded from a sparse parameterization and the other from a dense parameterization (i.e., one configured to retain fewer strata and one configured to retain more).

### Depth Proportional Resolution Algorithm

The depth proportional resolution algorithm drops half of retained strata when a threshold size cap is met in order to maintain `O(1)` space complexity.
Retained strata are evenly spaced.

| Sparse Parameterization                                                                                                                                                                                                                                                                                                | Dense Parameterization                                                                                                                                                                                                                                                                                                 |
| ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [![](docs/assets/a=policy_panel_plot+num_generations=256+policy=depth-proportional-resolution-stratum-retention-algorithm-resolution-2+ext=.gif)](docs/assets/a=policy_panel_plot+num_generations=256+policy=depth-proportional-resolution-stratum-retention-algorithm-resolution-2+ext=.gif)            | [![](docs/assets/a=policy_panel_plot+num_generations=256+policy=depth-proportional-resolution-stratum-retention-algorithm-resolution-8+ext=.gif)](docs/assets/a=policy_panel_plot+num_generations=256+policy=depth-proportional-resolution-stratum-retention-algorithm-resolution-8+ext=.gif)            |
| [![](docs/assets/num_generations=256+policy=depth-proportional-resolution-stratum-retention-algorithm-resolution-2+viz=stratum-retention-dripplot+ext=.png)](docs/assets/num_generations=256+policy=depth-proportional-resolution-stratum-retention-algorithm-resolution-2+viz=stratum-retention-dripplot+ext=.png) | [![](docs/assets/num_generations=256+policy=depth-proportional-resolution-stratum-retention-algorithm-resolution-8+viz=stratum-retention-dripplot+ext=.png)](docs/assets/num_generations=256+policy=depth-proportional-resolution-stratum-retention-algorithm-resolution-8+viz=stratum-retention-dripplot+ext=.png) |

#### Dense Parameterization Detail
| Num Strata Retained                                                                                                                                                                                                                                                                                            | Absolute MRCA Uncertainty by Position                                                                                                                                                                                                                                                                                                                              | Relative MRCA Uncertainty by Position                                                                                                                                                                                                                                                                                         |
| ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [![](docs/assets/num_generations=256+policy=depth-proportional-resolution-stratum-retention-algorithm-resolution-8+viz=strata-retained-num-lineplot+ext=.png)](docs/assets/num_generations=256+policy=depth-proportional-resolution-stratum-retention-algorithm-resolution-8+viz=strata-retained-num-lineplot+ext=.png) | [![](docs/assets/num_generations=256+policy=depth-proportional-resolution-stratum-retention-algorithm-resolution-8+viz=mrca-uncertainty-absolute-barplot+ext=.png)](docs/assets/num_generations=256+policy=depth-proportional-resolution-stratum-retention-algorithm-resolution-8+viz=mrca-uncertainty-absolute-barplot+ext=.png) | [![](docs/assets/num_generations=256+policy=depth-proportional-resolution-stratum-retention-algorithm-resolution-8+viz=mrca-uncertainty-relative-barplot+ext=.png)](docs/assets/num_generations=256+policy=depth-proportional-resolution-stratum-retention-algorithm-resolution-8+viz=mrca-uncertainty-relative-barplot+ext=.png) |

### Tapered Depth Proportional Resolution Algorithm

The tapered depth proportional resolution algorithm drops strata gradually from the rear once the threshold size cap is met (instead of purging half of strata all at once).

| Sparse Parameterization                                                                                                                                                                                                                                                                                                        | Dense Parameterization                                                                                                                                                                                                                                                                                                         |
| ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| [![](docs/assets/a=policy_panel_plot+num_generations=256+policy=tapered-depth-proportional-resolution-stratum-retention-algorithm-resolution-1+ext=.gif)](docs/assets/a=policy_panel_plot+num_generations=256+policy=tapered-depth-proportional-resolution-stratum-retention-algorithm-resolution-1+ext=.gif)            | [![](docs/assets/a=policy_panel_plot+num_generations=256+policy=tapered-depth-proportional-resolution-stratum-retention-algorithm-resolution-7+ext=.gif)](docs/assets/a=policy_panel_plot+num_generations=256+policy=tapered-depth-proportional-resolution-stratum-retention-algorithm-resolution-7+ext=.gif)            |
| [![](docs/assets/num_generations=256+policy=tapered-depth-proportional-resolution-stratum-retention-algorithm-resolution-1+viz=stratum-retention-dripplot+ext=.png)](docs/assets/num_generations=256+policy=tapered-depth-proportional-resolution-stratum-retention-algorithm-resolution-1+viz=stratum-retention-dripplot+ext=.png) | [![](docs/assets/num_generations=256+policy=tapered-depth-proportional-resolution-stratum-retention-algorithm-resolution-7+viz=stratum-retention-dripplot+ext=.png)](docs/assets/num_generations=256+policy=tapered-depth-proportional-resolution-stratum-retention-algorithm-resolution-7+viz=stratum-retention-dripplot+ext=.png) |

#### Dense Parameterization Detail
| Num Strata Retained                                                                                                                                                                                                                                                                                            | Absolute MRCA Uncertainty by Position                                                                                                                                                                                                                                                                                                                              | Relative MRCA Uncertainty by Position                                                                                                                                                                                                                                                                                         |
| -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [![](docs/assets/num_generations=256+policy=tapered-depth-proportional-resolution-stratum-retention-algorithm-resolution-7+viz=strata-retained-num-lineplot+ext=.png)](docs/assets/num_generations=256+policy=tapered-depth-proportional-resolution-stratum-retention-algorithm-resolution-7+viz=strata-retained-num-lineplot+ext=.png) | [![](docs/assets/num_generations=256+policy=tapered-depth-proportional-resolution-stratum-retention-algorithm-resolution-7+viz=mrca-uncertainty-absolute-barplot+ext=.png)](docs/assets/num_generations=256+policy=tapered-depth-proportional-resolution-stratum-retention-algorithm-resolution-7+viz=mrca-uncertainty-absolute-barplot+ext=.png) | [![](docs/assets/num_generations=256+policy=tapered-depth-proportional-resolution-stratum-retention-algorithm-resolution-7+viz=mrca-uncertainty-relative-barplot+ext=.png)](docs/assets/num_generations=256+policy=tapered-depth-proportional-resolution-stratum-retention-algorithm-resolution-7+viz=mrca-uncertainty-relative-barplot+ext=.png) |

### Fixed Resolution Algorithm

The fixed resolution algorithm permanently retains every `n`th stratum, giving it linear `O(n)` space complexity and uniform distribution of retained strata.

| Sparse Parameterization                                                                                                                                                                                                                                                                                     | Dense Parameterization                                                                                                                                                                                                                                                                                     |
| ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [![](docs/assets/a=policy_panel_plot+num_generations=256+policy=fixed-resolution-stratum-retention-algorithm-resolution-128+ext=.gif)](docs/assets/a=policy_panel_plot+num_generations=256+policy=fixed-resolution-stratum-retention-algorithm-resolution-128+ext=.gif)            | [![](docs/assets/a=policy_panel_plot+num_generations=256+policy=fixed-resolution-stratum-retention-algorithm-resolution-32+ext=.gif)](docs/assets/a=policy_panel_plot+num_generations=256+policy=fixed-resolution-stratum-retention-algorithm-resolution-32+ext=.gif)            |
| [![](docs/assets/num_generations=256+policy=fixed-resolution-stratum-retention-algorithm-resolution-128+viz=stratum-retention-dripplot+ext=.png)](docs/assets/num_generations=256+policy=fixed-resolution-stratum-retention-algorithm-resolution-128+viz=stratum-retention-dripplot+ext=.png) | [![](docs/assets/num_generations=256+policy=fixed-resolution-stratum-retention-algorithm-resolution-32+viz=stratum-retention-dripplot+ext=.png)](docs/assets/num_generations=256+policy=fixed-resolution-stratum-retention-algorithm-resolution-32+viz=stratum-retention-dripplot+ext=.png) |

#### Dense Parameterization Detail
| Num Strata Retained                                                                                                                                                                                                                                                                                            | Absolute MRCA Uncertainty by Position                                                                                                                                                                                                                                                                                                                              | Relative MRCA Uncertainty by Position                                                                                                                                                                                                                                                                                         |
| ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [![](docs/assets/num_generations=256+policy=fixed-resolution-stratum-retention-algorithm-resolution-32+viz=strata-retained-num-lineplot+ext=.png)](docs/assets/num_generations=256+policy=fixed-resolution-stratum-retention-algorithm-resolution-32+viz=strata-retained-num-lineplot+ext=.png) | [![](docs/assets/num_generations=256+policy=fixed-resolution-stratum-retention-algorithm-resolution-32+viz=mrca-uncertainty-absolute-barplot+ext=.png)](docs/assets/num_generations=256+policy=fixed-resolution-stratum-retention-algorithm-resolution-32+viz=mrca-uncertainty-absolute-barplot+ext=.png) | [![](docs/assets/num_generations=256+policy=fixed-resolution-stratum-retention-algorithm-resolution-32+viz=mrca-uncertainty-relative-barplot+ext=.png)](docs/assets/num_generations=256+policy=fixed-resolution-stratum-retention-algorithm-resolution-32+viz=mrca-uncertainty-relative-barplot+ext=.png) |

### Geometric Sequence Nth Root Algorithm

The geometric sequence algorithm provides constant `O(1)` space complexity with recency-proportional distribution of retained strata.
To accomplish this, a fixed number `k` of fixed-cardinality subcomponents track `k` waypoints exponentially spaced backward from the most-recent stratum (i.e., spaced corresponding to the roots `0/k`, `1/k`, `2/k`, ..., `k/k`).

| Sparse Parameterization                                                                                                                                                                                                                                                                                                         | Dense Parameterization                                                                                                                                                                                                                                                                                                             |
| ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [![](docs/assets/a=policy_panel_plot+num_generations=256+policy=nth-root-geometric-sequence-stratum-retention-algorithm-degree-6-interspersal-2+ext=.gif)](docs/assets/a=policy_panel_plot+num_generations=256+policy=nth-root-geometric-sequence-stratum-retention-algorithm-degree-6-interspersal-2+ext=.gif)            | [![](docs/assets/a=policy_panel_plot+num_generations=256+policy=nth-root-geometric-sequence-stratum-retention-algorithm-degree-1024-interspersal-2+ext=.gif)](docs/assets/a=policy_panel_plot+num_generations=256+policy=nth-root-geometric-sequence-stratum-retention-algorithm-degree-1024-interspersal-2+ext=.gif)            |
| [![](docs/assets/num_generations=256+policy=nth-root-geometric-sequence-stratum-retention-algorithm-degree-6-interspersal-2+viz=stratum-retention-dripplot+ext=.png)](docs/assets/num_generations=256+policy=nth-root-geometric-sequence-stratum-retention-algorithm-degree-6-interspersal-2+viz=stratum-retention-dripplot+ext=.png) | [![](docs/assets/num_generations=256+policy=nth-root-geometric-sequence-stratum-retention-algorithm-degree-1024-interspersal-2+viz=stratum-retention-dripplot+ext=.png)](docs/assets/num_generations=256+policy=nth-root-geometric-sequence-stratum-retention-algorithm-degree-1024-interspersal-2+viz=stratum-retention-dripplot+ext=.png) |

#### Dense Parameterization Detail
| Num Strata Retained                                                                                                                                                                                                                                                                                            | Absolute MRCA Uncertainty by Position                                                                                                                                                                                                                                                                                                                              | Relative MRCA Uncertainty by Position                                                                                                                                                                                                                                                                                         |
| ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [![](docs/assets/num_generations=256+policy=nth-root-geometric-sequence-stratum-retention-algorithm-degree-1024-interspersal-2+viz=strata-retained-num-lineplot+ext=.png)](docs/assets/num_generations=256+policy=nth-root-geometric-sequence-stratum-retention-algorithm-degree-1024-interspersal-2+viz=strata-retained-num-lineplot+ext=.png) | [![](docs/assets/num_generations=256+policy=nth-root-geometric-sequence-stratum-retention-algorithm-degree-1024-interspersal-2+viz=mrca-uncertainty-absolute-barplot+ext=.png)](docs/assets/num_generations=256+policy=nth-root-geometric-sequence-stratum-retention-algorithm-degree-1024-interspersal-2+viz=mrca-uncertainty-absolute-barplot+ext=.png) | [![](docs/assets/num_generations=256+policy=nth-root-geometric-sequence-stratum-retention-algorithm-degree-1024-interspersal-2+viz=mrca-uncertainty-relative-barplot+ext=.png)](docs/assets/num_generations=256+policy=nth-root-geometric-sequence-stratum-retention-algorithm-degree-1024-interspersal-2+viz=mrca-uncertainty-relative-barplot+ext=.png) |

### Tapered Geometric Sequence Nth Root Algorithm

The tapered geometric sequence nth root algorithm maintains exactly-constant size at its vanilla counterpart's upper bound instead of fluctuating below that bound.
It is more computationally expensive than the vanilla geometric sequence nth root algorithm.

| Sparse Parameterization                                                                                                                                                                                                                                                                                                                 | Dense Parameterization                                                                                                                                                                                                                                                                                                                  |
| --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [![](docs/assets/a=policy_panel_plot+num_generations=256+policy=tapered-nth-root-geometric-sequence-stratum-retention-algorithm-degree-1-interspersal-2+ext=.gif)](docs/assets/a=policy_panel_plot+num_generations=256+policy=tapered-nth-root-geometric-sequence-stratum-retention-algorithm-degree-1-interspersal-2+ext=.gif)            | [![](docs/assets/a=policy_panel_plot+num_generations=256+policy=tapered-nth-root-geometric-sequence-stratum-retention-algorithm-degree-4-interspersal-2+ext=.gif)](docs/assets/a=policy_panel_plot+num_generations=256+policy=tapered-nth-root-geometric-sequence-stratum-retention-algorithm-degree-4-interspersal-2+ext=.gif)            |
| [![](docs/assets/num_generations=256+policy=tapered-nth-root-geometric-sequence-stratum-retention-algorithm-degree-1-interspersal-2+viz=stratum-retention-dripplot+ext=.png)](docs/assets/num_generations=256+policy=tapered-nth-root-geometric-sequence-stratum-retention-algorithm-degree-1-interspersal-2+viz=stratum-retention-dripplot+ext=.png) | [![](docs/assets/num_generations=256+policy=tapered-nth-root-geometric-sequence-stratum-retention-algorithm-degree-4-interspersal-2+viz=stratum-retention-dripplot+ext=.png)](docs/assets/num_generations=256+policy=tapered-nth-root-geometric-sequence-stratum-retention-algorithm-degree-4-interspersal-2+viz=stratum-retention-dripplot+ext=.png) |

#### Dense Parameterization Detail
| Num Strata Retained                                                                                                                                                                                                                                                                                            | Absolute MRCA Uncertainty by Position                                                                                                                                                                                                                                                                                                                              | Relative MRCA Uncertainty by Position                                                                                                                                                                                                                                                                                         |
| ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [![](docs/assets/num_generations=256+policy=tapered-nth-root-geometric-sequence-stratum-retention-algorithm-degree-4-interspersal-2+viz=strata-retained-num-lineplot+ext=.png)](docs/assets/num_generations=256+policy=tapered-nth-root-geometric-sequence-stratum-retention-algorithm-degree-4-interspersal-2+viz=strata-retained-num-lineplot+ext=.png) | [![](docs/assets/num_generations=256+policy=tapered-nth-root-geometric-sequence-stratum-retention-algorithm-degree-4-interspersal-2+viz=mrca-uncertainty-absolute-barplot+ext=.png)](docs/assets/num_generations=256+policy=tapered-nth-root-geometric-sequence-stratum-retention-algorithm-degree-4-interspersal-2+viz=mrca-uncertainty-absolute-barplot+ext=.png) | [![](docs/assets/num_generations=256+policy=tapered-nth-root-geometric-sequence-stratum-retention-algorithm-degree-4-interspersal-2+viz=mrca-uncertainty-relative-barplot+ext=.png)](docs/assets/num_generations=256+policy=tapered-nth-root-geometric-sequence-stratum-retention-algorithm-degree-4-interspersal-2+viz=mrca-uncertainty-relative-barplot+ext=.png) |

### Recency Proportional Resolution Algorithm

The recency proportional resolution algorithm maintains relative MRCA estimation error below a constant bound.
It exhibits logarithmic `O(log(n))` space complexity.

| Sparse Parameterization                                                                                                                                                                                                                                                                                                  | Dense Parameterization                                                                                                                                                                                                                                                                                                   |
| ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| [![](docs/assets/a=policy_panel_plot+num_generations=256+policy=recency-proportional-resolution-stratum-retention-algorithm-resolution-0+ext=.gif)](docs/assets/a=policy_panel_plot+num_generations=256+policy=recency-proportional-resolution-stratum-retention-algorithm-resolution-0+ext=.gif)            | [![](docs/assets/a=policy_panel_plot+num_generations=256+policy=recency-proportional-resolution-stratum-retention-algorithm-resolution-6+ext=.gif)](docs/assets/a=policy_panel_plot+num_generations=256+policy=recency-proportional-resolution-stratum-retention-algorithm-resolution-6+ext=.gif)             |
| [![](docs/assets/num_generations=256+policy=recency-proportional-resolution-stratum-retention-algorithm-resolution-0+viz=stratum-retention-dripplot+ext=.png)](docs/assets/num_generations=256+policy=recency-proportional-resolution-stratum-retention-algorithm-resolution-0+viz=stratum-retention-dripplot+ext=.png) | [![](docs/assets/num_generations=256+policy=recency-proportional-resolution-stratum-retention-algorithm-resolution-6+viz=stratum-retention-dripplot+ext=.png)](docs/assets/num_generations=256+policy=recency-proportional-resolution-stratum-retention-algorithm-resolution-6+viz=stratum-retention-dripplot+ext=.png) |

#### Dense Parameterization Detail
| Num Strata Retained                                                                                                                                                                                                                                                                                            | Absolute MRCA Uncertainty by Position                                                                                                                                                                                                                                                                                                                              | Relative MRCA Uncertainty by Position                                                                                                                                                                                                                                                                                         |
| -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [![](docs/assets/num_generations=256+policy=recency-proportional-resolution-stratum-retention-algorithm-resolution-6+viz=strata-retained-num-lineplot+ext=.png)](docs/assets/num_generations=256+policy=recency-proportional-resolution-stratum-retention-algorithm-resolution-6+viz=strata-retained-num-lineplot+ext=.png) | [![](docs/assets/num_generations=256+policy=recency-proportional-resolution-stratum-retention-algorithm-resolution-6+viz=mrca-uncertainty-absolute-barplot+ext=.png)](docs/assets/num_generations=256+policy=recency-proportional-resolution-stratum-retention-algorithm-resolution-6+viz=mrca-uncertainty-absolute-barplot+ext=.png) | [![](docs/assets/num_generations=256+policy=recency-proportional-resolution-stratum-retention-algorithm-resolution-6+viz=mrca-uncertainty-relative-barplot+ext=.png)](docs/assets/num_generations=256+policy=recency-proportional-resolution-stratum-retention-algorithm-resolution-6+viz=mrca-uncertainty-relative-barplot+ext=.png) |

### Curbed Recency Proportional Resolution Algorithm

The curbed recency-proportional resolution algorithm eagerly utilize fixed stratum storage capacity to minimize recency-proportional MRCA uncertainty.

This strategy provides the finest-possible recency-proportional granularity within parameterized space constraint.
Resolution degrades gracefully as deposition history grows.

This algorithm is similar to the geometric sequence nth root algorithm in guaranteeing constant space complexity with recency-proportional MRCA uncertainty.
However, this curbed recency-proportional algorithm makes fuller (i.e., more aggressive) use of available space during early depositions.

In this way, it is similar to the tapered geometric sequence nth root algorithm during early depositions.
The tapered nth root algorithm makes fullest use of fixed available space.
In fact, it perfectly fills available space.
However, the curbed recency-proportional algorithm's space use is more effective at early time points --- it better minimizes recency-proportional MRCA uncertainty than the curbed algorithm.

| Sparse Parameterization                                                                                                                                                                                                                                                                                                  | Dense Parameterization                                                                                                                                                                                                                                                                                                   |
| ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| [![](docs/assets/a=policy_panel_plot+num_generations=256+policy=curbed-recency-proportional-resolution-stratum-retention-algorithm-size-curb-19+ext=.gif)](docs/assets/a=policy_panel_plot+num_generations=256+policy=curbed-recency-proportional-resolution-stratum-retention-algorithm-size-curb-19+ext=.gif)            | [![](docs/assets/a=policy_panel_plot+num_generations=256+policy=curbed-recency-proportional-resolution-stratum-retention-algorithm-size-curb-79+ext=.gif)](docs/assets/a=policy_panel_plot+num_generations=256+policy=curbed-recency-proportional-resolution-stratum-retention-algorithm-size-curb-79+ext=.gif)             |
| [![](docs/assets/num_generations=256+policy=curbed-recency-proportional-resolution-stratum-retention-algorithm-size-curb-19+viz=stratum-retention-dripplot+ext=.png)](docs/assets/num_generations=256+policy=curbed-recency-proportional-resolution-stratum-retention-algorithm-size-curb-19+viz=stratum-retention-dripplot+ext=.png) | [![](docs/assets/num_generations=256+policy=curbed-recency-proportional-resolution-stratum-retention-algorithm-size-curb-79+viz=stratum-retention-dripplot+ext=.png)](docs/assets/num_generations=256+policy=curbed-recency-proportional-resolution-stratum-retention-algorithm-size-curb-79+viz=stratum-retention-dripplot+ext=.png) |

#### Dense Parameterization Detail
| Num Strata Retained                                                                                                                                                                                                                                                                                            | Absolute MRCA Uncertainty by Position                                                                                                                                                                                                                                                                                                                              | Relative MRCA Uncertainty by Position                                                                                                                                                                                                                                                                                         |
| -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [![](docs/assets/num_generations=256+policy=curbed-recency-proportional-resolution-stratum-retention-algorithm-size-curb-79+viz=strata-retained-num-lineplot+ext=.png)](docs/assets/num_generations=256+policy=curbed-recency-proportional-resolution-stratum-retention-algorithm-size-curb-79+viz=strata-retained-num-lineplot+ext=.png) | [![](docs/assets/num_generations=256+policy=curbed-recency-proportional-resolution-stratum-retention-algorithm-size-curb-79+viz=mrca-uncertainty-absolute-barplot+ext=.png)](docs/assets/num_generations=256+policy=curbed-recency-proportional-resolution-stratum-retention-algorithm-size-curb-79+viz=mrca-uncertainty-absolute-barplot+ext=.png) | [![](docs/assets/num_generations=256+policy=curbed-recency-proportional-resolution-stratum-retention-algorithm-size-curb-79+viz=mrca-uncertainty-relative-barplot+ext=.png)](docs/assets/num_generations=256+policy=curbed-recency-proportional-resolution-stratum-retention-algorithm-size-curb-79+viz=mrca-uncertainty-relative-barplot+ext=.png) |

This policy works by splicing together successively-sparser
`recency_proportional_resolution_algo` paramaterizations then a
permanently fixed parameterization of the `geometric_seq_nth root` algorithm.
Sparsification occurs when upper bound space use increases to exceed the fixed-size available capacity.
For a very sparse paramaterization with a size cap of eight strata, shown below, the transition to `geometric_seq_nth_root_ago` can be seen at generation 129.

| Very Sparse Parameterization | |
|------------------------------|-|
| [<img src="docs/assets/a=policy_panel_plot+num_generations=256+policy=curbed-recency-proportional-resolution-stratum-retention-algorithm-size-curb-8+ext=.gif" width=450>](docs/assets/a=policy_panel_plot+num_generations=256+policy=curbed-recency-proportional-resolution-stratum-retention-algorithm-size-curb-9+ext=.gif) | ![docs/assets/num_generations=256+policy=curbed-recency-proportional-resolution-stratum-retention-algorithm-size-curb-8+viz=stratum-retention-dripplot+ext=.png](docs/assets/num_generations=256+policy=curbed-recency-proportional-resolution-stratum-retention-algorithm-size-curb-8+viz=stratum-retention-dripplot+ext=.png) |

_Note: minor changes have been made to the transition points of the curbed-recency proportional resolution algorithm, but these older graphics best convey the underlying concept behind the algorithm._

#### Very Sparse Parameterization Detail
| Num Strata Retained                                                                                                                                                                                                                                                                                            | Absolute MRCA Uncertainty by Position                                                                                                                                                                                                                                                                                                                              | Relative MRCA Uncertainty by Position                                                                                                                                                                                                                                                                                         |
| -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [![](docs/assets/num_generations=256+policy=curbed-recency-proportional-resolution-stratum-retention-algorithm-size-curb-8+viz=strata-retained-num-lineplot+ext=.png)](docs/assets/num_generations=256+policy=curbed-recency-proportional-resolution-stratum-retention-algorithm-size-curb-8+viz=strata-retained-num-lineplot+ext=.png) | [![](docs/assets/num_generations=256+policy=curbed-recency-proportional-resolution-stratum-retention-algorithm-size-curb-8+viz=mrca-uncertainty-absolute-barplot+ext=.png)](docs/assets/num_generations=256+policy=curbed-recency-proportional-resolution-stratum-retention-algorithm-size-curb-8+viz=mrca-uncertainty-absolute-barplot+ext=.png) | [![](docs/assets/num_generations=256+policy=curbed-recency-proportional-resolution-stratum-retention-algorithm-size-curb-8+viz=mrca-uncertainty-relative-barplot+ext=.png)](docs/assets/num_generations=256+policy=curbed-recency-proportional-resolution-stratum-retention-algorithm-size-curb-8+viz=mrca-uncertainty-relative-barplot+ext=.png) |


## Citing

If `hstrat` software or hereditary stratigraphy methodology contributes to a scholarly work, please cite it according to references provided [here](https://hstrat.readthedocs.io/en/latest/citing.html).
We would love to list your project using `hstrat` in our documentation, see more [here](https://hstrat.readthedocs.io/en/latest/projects.html).

## Credits

This package was created with Cookiecutter and the `audreyr/cookiecutter-pypackage` project template.

## hcat

![hcat](docs/assets/hcat-banner.png)
