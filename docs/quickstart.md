## Quickstart

The goal of this software is to enable approximate inference of the phylogenetic history of a distributed digital population solely through analysis of heritable genome annotations. Put another way, given a scenario where packets of data are being copied and moved within a distributed system, this software enables estimation of how closely any two data packets are related. More precisely, for any two extant data packets, estimation bounds can be produced for the number of copies elapsed from those packets’ last shared source copy (i.e., most recent common ancestor a.k.a. MRCA) to yield each extant packet. This is done by means of annotations on the data being copied itself — no centralized tracking system required.

This capability has direct applications in digital evolution research (e.g., artificial life, genetic programming, genetic algorithms), and also may prove useful for other distributed systems applications.

### Using hstrat
```$ python3 -m pip install hstrat```

All library components can be accessed directly from the convenience flat namespace `hstrat.hstrat`

### Getting Started

In order to track the data (referred to as *stratum*) deposited at each generation, we can use an annotation called a *hereditary stratigraphic column*.
```
from hstrat import hstrat

founder1 = hstrat.HereditaryStratigraphicColumn(
    stratum_retention_policy=hstrat.fixed_resolution_algo.Policy(1)
)
founder2 = hstrat.HereditaryStratigraphicColumn(
    stratum_retention_policy=hstrat.fixed_resolution_algo.Policy(3),
)
```
For each annotation, a specific *stratum retention policy* can be chosen. Simply put, these are various methods use follow a specific algorithm to "prune", or systematically delete, data in the column to avoid a linear space complexity. As a downside, pruning results in uncertainty in MRCA generation estimates.

 In the example above, the algorithm `fixed_resolution_algo` was chosen. The specific policy instance is supplied an integer that dictates the amount of pruning, with smaller values resulting in denser stratum retention. For example, a policy using the fixed resolution algorithm supplied with the value three would retain  strata from every third generation.

 Below is a quick overview of the five available algorithms. For a more in depth overview, visit [Choosing a Retention Policy](./policies.html).


| Stratum Retention Algorithm               | Space Complexity | MRCA Gen Uncertainty |
| ----------------------------------------- | ---------------- | -------------------- |
| Fixed Resolution Algorithm                | `n/k`            | `k`                  |
| Recency-proportional Resolution Algorithm | `k * log(n)`     | `m/k`                |
| Depth-proportional Resolution Algorithm   | `k`              | `n/k`                |
| Geometric Sequence Nth Root Algorithm     | `k`              | `m * n^(1/k)`        |
| Curbed Recency-proportional Resolution Algorithm | `k`     | `m / k` -> `m * n^(1/k)` |

### Estimating MCRA
To check for common ancestors between two columns:
```
print(
    hstrat.does_have_any_common_ancestor(founder1, founder2)
) # -> False
```

In order for two columns to have a common ancestor, one of the columns must be created from another. This can be accomplished using the `Clone()` method. The `CloneDescendant()` and `CloneNthDescendant(n)` methods are also available, cloning and then depositing one and n descendants respectively.

```
descendant2a = founder2.Clone()
for __ in range(10): descendant2a.DepositStratum()

descendant2b = descendant2a.CloneDescendant()
descendant2c = descendant2a.CloneNthDescendant(20)

print(
    hstrat.does_have_any_common_ancestor(founder2, descendant2a)
) # -> True
```

A new generation of stratum can be added by running `DepositStratum()` on specific hereditary stratigraphic columns. To elapse multiple generations , `DepositStrata()` can also be used, taking in an integer to specify the number of generations elapsed.

If you want to find the number of generations elapsed since the MRCA, `calc_ranks_since_mrca_bounds_with` will return a tuple with the estimated lower and upper bound. The argument `prior` represents the prior probability density distribution over possible generations of the MRCA.
<!-- what does this mean? -->
```
print(
  hstrat.calc_ranks_since_mrca_bounds_with(
    descendant2b, descendant2c, prior="arbitrary",
  )
) # -> (0, 3)

print(
  hstrat.calc_ranks_since_mrca_bounds_with(
    descendant2c, descendant2b, prior="arbitrary",
  )
) # -> (19, 22)

print(
  hstrat.calc_rank_of_mrca_bounds_between(
    descendant2b, descendant2c, prior="arbitrary"
  ),
) # -> (9, 12)
```

### Creating and Using Populations

A genome can be defined with a user-created class, with a specific attribute containing the annotation for each instance. Using this class, a population of the genome can be created by instantiating  a list of objects.

An easier way to generate a population of hereditary stratigraphic columns is from a biopython tree using `descend_template_phylogeny_biopython`.
```
template_tree = BioPhylo.read(f"{assets_path}/example.newick", "newick")
template_tree.rooted = True

extant_population = hstrat.descend_template_phylogeny_biopython(
    template_tree,
    seed_column=hstrat.HereditaryStratigraphicColumn(
        hstrat.recency_proportional_resolution_algo.Policy(5)
    ),
)
```
This list can be used to test tree reconstruction on, similar to the results of an actual phlyogenetic simulation. The function `build_tree` takes in a population and returns a tree constructed in alife standard format. The `version_pin` parameter dictates how calls to the function should resolve in future releases, with `hstrat.__version__` automatically tracking new updates.
```
estimated_phylogeny = hstrat.build_tree(
        extant_population,
        version_pin=hstrat.__version__,
)
```

### Reading and Displaying Columns
An ascii representation of a hereditary stratigraph column can be printed using the `hstrat.col_to_ascii()` function, passing in the specified column as a parameter.
```
hstrat.fixed_resolution_algo.Policy(3),

col = hstrat.HereditaryStratigraphicColumn(
  stratum_retention_policy=hstrat.fixed_resolution_algo.Policy(3),
)

for __ in range(5):
    col.DepositStratum()

print(hstrat.col_to_ascii(col))
```
produces the following:
```
+----------------------------------------------------+
|                    MOST ANCIENT                    |
+--------------+---------------+---------------------+
| stratum rank | stratum index | stratum differentia |
+--------------+---------------+---------------------+
|      0       |       0       |  -4cde7c967ba79426* |
+--------------+---------------+---------------------+
|      1       | ░░░░░░░░░░░░░ | ░░░░░░░░░░░░░░░░░░░ |
+--------------+---------------+---------------------+
|      2       | ░░░░░░░░░░░░░ | ░░░░░░░░░░░░░░░░░░░ |
+--------------+---------------+---------------------+
|      3       |       1       |  -a2c09b3da6cc8ed*  |
+--------------+---------------+---------------------+
|      4       | ░░░░░░░░░░░░░ | ░░░░░░░░░░░░░░░░░░░ |
+--------------+---------------+---------------------+
|      5       |       2       |  -681f396ad85c5f0e* |
+--------------+---------------+---------------------+
|                    MOST RECENT                     |
+----------------------------------------------------+
*: stored in stratum (otherwise calculated)
░: discarded stratum
```

A column can also be exported to pandas dataframe.
```
policy = hstrat.recency_proportional_resolution_algo.Policy(3)

    col = hstrat.HereditaryStratigraphicColumn(
        stratum_retention_policy=policy,
    )
    for __ in range(100):
        col.DepositStratum()

    print(hstrat.col_to_dataframe(col))
```
produces the following:
```
    index  rank          differentia
0       0     0 -6180956281275397382
1       1    16 -4554867789198945161
2       2    32 -8297832136108013558
3       3    48 -4767082307141677512
4       4    56  5724569898664146544
5       5    64 -9216255470933076657
6       6    72  7881635762195015486
7       7    76 -4772273942592251779
8       8    80  7625591022615046411
9       9    84 -7808776422708359210
10     10    88 -1987170610874028582
11     11    90 -4019547956382824548
12     12    92 -3683760008805748268
13     13    94  6230285586143489737
14     14    95  6628593771172131734
15     15    96  6580751823188128345
16     16    97  7228462793392828043
17     17    98  8962966579506364754
18     18    99  6922710967904506264
19     19   100 -3907787533844485358
```
### Further Reading
- [Choosing a Retention Policy](./policies.html)
- [Surface repository](https://github.com/mmore500/hstrat-surface-concept/tree/master)
