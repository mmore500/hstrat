---
title: 'hstrat: a Python Package for phylogenetic inference on distributed digital evolution populations'
tags:
  - Python
  - artificial life
  - digital evolution
  - distributed computing
authors:
  - name: Matthew Andres Moreno
    orcid: 0000-0003-4726-4479
    affiliation: 1
  - name: Emily Dolson
    orcid: 0000-0001-8616-4898
    affiliation: 1
  - name: Charles Ofria
    orcid: 0000-0003-2924-1732
    affiliation: 1
affiliations:
 - name: Michigan State University
   index: 1
date: 1 October 2022
bibliography: paper.bib
---

# Summary

Digital evolutions systems instantiate evolutionary processes over populations of virtual agents *in silico*.
Such systems help expand evolutionary theory and can be used to solve applied heuristic optimization problems.
Digital evolution will benefit greatly by continuing to capitalize on profound advances in parallel and distributed computing [CITE], particularly emerging unconventional computing architectures [CITE].
However, scaling up digital evolution presents many challenges; here, we focus on the problem of record keeping of evolutionary history across vast and potentially unreliable hardware networks.

The `hstrat` Python library exists to facilitate application of hereditary stratigraphy, a cutting-edge technique to enable phylogenetic inference over distributed digital evolution populations [@moreno2022hereditary].
This technique departs from the traditional perfect-tracking approach to phylogenetic record-keeping.
Instead, hereditary stratigraphy enables phylogenetic history to be inferred from heritable annotations attached to evolving digital agents.
This approach aligns with phylogenetic reconstruction methodologies in evolutionary biology [CITE].
Hereditary stratigraphy attaches a set of immutable historical "checkpoints" --- referred to as _strata_ --- as an annotation on evolving genomes.
Checkpoints can be strategically discarded to reduce annotation size at the cost of increasing inference uncertainty.
A particular strategy for which checkpoints to discarded when is referred to as a _stratum retention policy_.
We refer to the set of retained strata as a _hereditary stratigraphic colum_.

Appropriate stratum retention policy choice varies by application.
For example, if annotation size is not a concern it may be best to preserve all strata.
In other situations, it may be necessary to constrain annotation size to remain within a fixed memory budget.

Key features of the library include:

- object-oriented hereditary stratigraphic column implementation to annotate arbitrary genomes,
- modular interchangeability and user extensibility of stratum retention policies,
- programmatic interface to query guarantees and behavior of stratum retention policy,
- modular interchangeability and user extensibility of back-end data structure used to store annotation data,
- a suite of visualization tools to elucidate stratum retention policies,
- support for automatic parameterization of stratum retention policies to meet user size complexity or inference precision specifications,
- tools to compare two columns and extract information about the phylogenetic relationship between them,
- [extensive documentation](https://hstrat.readthedocs.io) hosted on [ReadTheDocs](https://readthedocs.io),
- a comprehensive test suite to ensure stability and reliability,
- convenient availability as a Python package via the [PyPI repository](https://pypi.org/), and
- pure Python implementation to ensure universal portability.

# Statement of Need

The `hstrat` software exists to equip parallel and distributed evolution digital systems --- simulations that instantiate the process of evolution in an agent-based framework --- with phylogenetic tracking capabilities.
Parallel and distributed computation exponentiates the power of digital evolution by allowing for larger populations, more generations, more sophisticated genotype-phenotype mappings, and more robust fitness functions [CITE]
Indeed, several notable projects within the field have successfully exploited massively parallel and distributed computational resources [CITE CARL SIMMSS; SENTIENT; others].
Further development of methodology and software such as this work will position the field to continue leveraging ongoing advances in computing hardware.

The capability to detect phylogenetic cues within digital evolution has become increasingly necessary in both applied and scientific contexts.
These cues unlock _post hoc_ insight into evolutionary history --- particularly with respect to ecology and selection pressure --- but also can be harnessed to drive digital evolution algorithms as they unfold [CITE].
However, parallel and distributed evaluation complicates, among other concerns, maintenance of an evolutionary record.
Existing phylogenetic record keeping requires inerrant and complete collation of birth and death reports within a centralized data structure.
Such perfect tracking approaches are brittle to data loss or corruption and impose communication overhead.

Hereditary stratigraphy methodology, and the implementing `hstrat` software library, furnishes demand for efficient, tractable, and robust phylogenetic inference at scale.
This approach exchanges a centralized perfect record of history for a process where history is estimated from comparison of available extant genomes, aligning with the paradigm of phylogenetic inference in wet biology.

Although targeted to digital evolution use cases, impact of our work extends beyond to the various applications of digital evolution.
Evolutionary biology poses uniquely abstract, nuanced, and nebulous questions, such as the origins of life and the evolution of complexity [CITE].
Computational modeling provides one foothold for such inquiry, particularly with respect to phenomena that typically unfold on geological timescales or hypotheses that invoke counterfactuals outside the bounds of physical reality [CITE].
Elsewhere, in the realm of computational optimization, heuristic algorithms provide a foothold to explore high-dimensional and deceptive search spaces [CITE].
Improvements to distributed phylogenetic tracking can benefit both of these niches, providing means to test more sophisticated evolutionary hypotheses and means to discover better solutions to hard problems.

In addition to its founding purview within digital evolution, we anticipate hereditary stratigraphy --- and this software implementation --- may find applications within other domains of distributed computing.
For example, hereditary stratigraphy could equip a population protocol system with the capability for on-the-fly estimation of the relationship between descendants of a forking message chain or a forking process tree [@angluin2005power, @aspnes2009introduction].

Across all these domains, free availability of the `hstrat` software will play a central role in bringing hereditary stratigraphy methodology into practice.
Library development incorporates intentional design choices to promote successful outside use, including

- modular, hierarchical, well-named, and consistent API,
- comprehensive and application-oriented documentation,
- "batteries included" provision of many stratum retention policy options covering a wide variety of use cases,
- declarative configuration interfaces (i.e., automatic parameterization), and
- emphasis on user extensibility without modification of core library code.

# Projects Using the Software

A pre-release version of this software was used to perform experiments, validate derivations, and create visualizations for the conference article introducing the method of hereditary stratigraphy [@moreno2022hereditary].

A native version of this software is being incorporated into the next version of DISHTINY, a digital framework for studying evolution of multicellularity [@moreno2019toward; @moreno2021exploring; @moreno2021case].
We also anticipate making this software available through the Modular Agent Based Evolution framework as a community-contributed component [@bohm2019mabe].

# Future Work

The `hstrat` project remains under active development.

A major next objective for the `hstrat` project will be development of a header-only C++ library to complement the Python library presented here.
This implementation will improve memory and CPU efficiency as well as better integrating with many scientific computing or embedded systems applications, which often employ native code to meet performance requirements.

This direction opens the possibility of adding support for other high-level languages in the future [@beazley2003automated].
Indeed, at a minimum, we plan to update the Python library to include support for wrapped these native components [@pybind11].
However, the pure Python implementation will remain as a fallback for platforms lacking native support.

As released in version 1.0.1, the `hstrat` library contains a comprehensive set of tools to perform pairwise comparisons between extant hereditary stratigraphic columns.
However, a key use case for the library will be phylogenetic reconstruction over entire populations.
We plan to expand the library to add tools for population-level phylogenetic reconstruction and visualization in future releases.

Although, as currently released, `hstrat` does support serialization and de-serialization via Python's pickle protocol, which suffices for data storage and transfer within and between Python contexts, human-readable and binary serialization formats intercompatible outside of Python will be crucial.

# Acknowledgements

This research was supported in part by NSF grants DEB-1655715 and DBI-0939454 as well as by Michigan State University through the computational resources provided by the Institute for Cyber-Enabled Research.
This material is based upon work supported by the National Science Foundation Graduate Research Fellowship under Grant No. DGE-1424871.
Any opinions, findings, and conclusions or recommendations expressed in this material are those of the author(s) and do not necessarily reflect the views of the National Science Foundation.

# References

<div id="refs"></div>

\pagebreak
\appendix
