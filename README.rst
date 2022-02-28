============
hstrat
============


.. image:: https://img.shields.io/pypi/v/hstrat.svg
        :target: https://pypi.python.org/pypi/hstrat

.. image:: https://img.shields.io/travis/mmore500/hstrat.svg
        :target: https://travis-ci.com/mmore500/hstrat

.. image:: https://readthedocs.org/projects/hstrat/badge/?version=latest
        :target: https://hstrat.readthedocs.io/en/latest/?badge=latest
        :alt: Documentation Status




hstrat enables phylogenetic inference on distributed digital evolution populations



* Free software: MIT license
* Documentation: https://hstrat.readthedocs.io.


.. code-block:: python3

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


Credits
-------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
