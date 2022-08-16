# hstrat

[
  ![PyPi](https://img.shields.io/pypi/v/hstrat.svg)
](https://pypi.python.org/pypi/hstrat)
[
  ![Travis CI](https://img.shields.io/travis/mmore500/hstrat.svg)
](https://travis-ci.com/mmore500/hstrat)
[
  ![Read The Docs](https://readthedocs.org/projects/hstrat/badge/?version=latest)
](https://hstrat.readthedocs.io/en/latest/?badge=latest)

hstrat enables phylogenetic inference on distributed digital evolution populations

* Free software: MIT license
* Documentation: <https://hstrat.readthedocs.io>

## Usage

```python3
from hstrat import hstrat

individual1 = hstrat.HereditaryStratigraphicColumn()
individual2 = hstrat.HereditaryStratigraphicColumn()

individual1_child1 = individual1.CloneDescendant()

individual1.HasAnyCommonAncestorWith(individual2) # -> False
individual1_child1.HasAnyCommonAncestorWith(individual2) # -> False

individual1_grandchild1 = individual1_child1.CloneDescendant()
individual1_grandchild2 = individual1_child1.CloneDescendant()

individual1_grandchild1.CalcRankOfMrcaBoundsWith(
  individual1_grandchild2,
) # -> (1, 2)
```

customize policy

## Credits

This package was created with Cookiecutter and the `audreyr/cookiecutter-pypackage` project template.
