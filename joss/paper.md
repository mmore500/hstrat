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

Digital evolution, simulation that instantiates evolutionary processes over populations of virtual agents, avails both theoretical evolutionary biology and applied heuristic optimization engineering.
Digital evolution will benefit greatly by continuing to capitalize on profound advances in parallel and distributed computing [CITE], particularly emerging unconventional computing architectures [CITE].
However, scaling up digital evolution presents many challenges --- one of them being managing record keeping of evolutionary history across vast and potentially unreliable hardware networks.

Hereditary stratigraphy is a recently-developed technique to enable phylogenetic inference over distributed digital evolution populations [@moreno2022hereditary].
This technique departs from the traditional perfect-tracking approach.
Instead, hereditary stratigraphy enables phylogenetic history to be inferred from heritable annotations attached to evolving digital agents.
This approach aligns with established notions of phylogenetic reconstruction in evolutionary biology [CITE].
Unlike a typical neutral drift model where genomes diverge under stochastic perturbation, hereditary stratigraphy attaches a set of immutable historical "checkpoints" --- referred to as _strata_ --- as an annotation evolving genomes.
Checkpoints can be discarded to reduce annotation size at the cost of increasing inference uncertainty.
Thus, direct, flexible trade-offs between annotation size and inference precision can be made by adjusting which checkpoints are discarded when.
A particular trade-off choice is referred to as a _stratum retention policy_.

The `hstrat` Python library exists to facilitate application of hereditary stratigraphy methodology.
Key features of the library include:

- a comprehensive test suite to ensure stability and reliability,
- convenient availability as a Python package via the PyPi repository,
- extensive documentation hosted on [ReadTheDocs](https://readthedocs.io), including
  - a quick start guide,
  - a developer-oriented recap of the hereditary stratigraphy method,
  - a catalog of available stratum retention policies, and
  - a full API reference,
- modular interchangeability and user extensibility of stratum retention policies,
- programmatic interface to query guarantees and behavior of stratum retention policy,
- modular interchangeability and user extensibility of back-end data structure used to store annotation data,
- pure Python implementation to ensure universal portability,
- a suite of visualization tools to elucidate stratum retention policies,
- support for automatic parameterization of stratum retention policies to meet user size complexity or inference precision specifications, and
- tools to compare two columns and extract information about phylogenetic relationship between them.

# Statement of Need

Evolutionary biologists often grapple with abstract, nuanced, and difficult questions, such as the origins of life, evolution of complexity, and the evolution of aging and mortality [CITE].
Mathematical and computational modeling provides one foothold for such inquiry, particularly with respect to phenomena that typically unfold on geological timescales or hypotheses that invoke counterfactuals outside the bounds of physical reality [CITE].
Elsewhere, in the realm of computational optimization, heuristic algorithms provide a foothold to extract high quality solutions from difficult high-dimension, deceptive search spaces [CITE].

Digital evolution --- simulations that instantiate the process of evolution within an agent-based framework --- straddles both of these niches, providing means to test sophisticated evolutionary hypotheses and means to discover good solutions to hard problems.
These simulations benefit greatly from parallel and distributed computation, which provide means to provision larger populations, run more generations, employ more sophisticated genotype-phenotype mappings, and evaluate more nuanced fitness functions [CITE].
Indeed, several notable projects within the field have successfully exploited massively parallel and distributed computational resources [CITE].
As the field of digital evolution progresses in tandem with advances in computing hardware proliferates, methodology --- and accompanying software --- to enable scale up of digital evolution will remain a key priority.

Advances in theory and methodology have made the capability to detect phylogenetic cues within digital evolution has become increasingly valuable in both applied and scientific contexts.
These cues unlock _post hoc_ insight into evolutionary history --- particularly with respect to ecology and selection pressure --- but also can be harnessed drive digital evolution algorithms as they unfold [CITE].
However, parallel and distributed simulation complicates, among other concerns, maintenance of an evolutionary record.
Existing work with phylogenetic analysis typically employs a tracking model, which requires perfect and complete collation of birth and death reports within a centralized data structure.

Hereditary stratigraphy methodology, and the implementing `hstrat` software library, furnishes demand for efficient, tractable, and robust phylogenetic inference at scale.
This approach exchanges a centralized perfect record of history for a process where history is estimated from comparison of available extant genomes, much as is the case in wet biology.

In addition to its autochthonous purview within digital evolution, we anticipate hereditary stratigraphy --- and this software implementation --- may find applications within other domains of distributed computing.
For example, hereditary stratigraphy could equip a population protocol system with the capability for on-the-fly estimation of the relationship between specimens from a forking message chain or a forking process tree [@angluin2005power, @aspnes2009introduction].

Across all these domains, free availability of the `hstrat` software will play a central role in bringing hereditary stratigraphy methodology into practice.
Library development incorporates intentional design choices to promote successful outside use, including

- modular, hierarchical, well-named, and consistent API,
- comprehensive and application-oriented documentation,
- "batteries included" provision of many stratum retention policy options covering a wide variety of use cases,
- declarative configuration interfaces (i.e., automatic parameterization), and
- emphasis on user extensibility without modification of library code.

# Projects Using the Software

A pre-release version of this software was used to perform experiments, validate MATH, and create visualizations for the conference article introducing the method of hereditary stratigraphy [@moreno2022hereditary].

A native version of this software will be incorporated for use in the next version of DISHTINY, a digital framework for studying evolution of multicellularity [@moreno2019toward; @moreno2021exploring; @moreno2021case].
We also anticipate making this software available through the Modular Agent Based Evolution as community-contributed component [@bohm2019mabe].

# Future Work

The `hstrat` project remains under active development.
We anticipate in the near- and longer-term future to enhance and complement the Python package focused on in this text.

A major next objective for the `hstrat` project will be development of a header-only C++ library.
This implementation will improve memory and CPU efficiency as well as better integrating with scientific computing or embedded systems applications, which typically employ native code to meet performance requirements.

This direction opens the possibility of adding support for `hstrat` other high-level languages in the future [@beazley2003automated].
In particular, we intend to expose a native `hstrat` implementation through the existing Python interface by preparation of wrapper code [@pybind11].
However, pure Python implementation will remain as a fallback for platforms lacking native support.
We anticipate that most pure Python components will remain in common use after the future release of a C++ library due to their versatility, readability, and extensibility --- particularly as a vehicle for _post hoc_ phylogenetic analysis.

As released in version 1.0.1, the `hstrat` library contains a comprehensive set of tools to perform pairwise comparisons between extant hereditary stratigraphic columns.
However, a key use case for the library will be phylogenetic reconstruction over entire populations.
We plan to expand the library to add tools for population-level phylogenetic reconstruction and visualization in future releases.

Although, as currently released, `hstrat` does support serialization and de-serialization via Python's pickle protocol, which suffices for data storage and transfer within and between Python contexts, intercompatible human-readable and binary serialization formats will be crucial to implementation of and interoperation with a C++ `hstrat` library.

# Acknowledgements

This research was supported in part by NSF grants DEB-1655715 and DBI-0939454 as well as by Michigan State University through the computational resources provided by the Institute for Cyber-Enabled Research.
This material is based upon work supported by the National Science Foundation Graduate Research Fellowship under Grant No. DGE-1424871.
Any opinions, findings, and conclusions or recommendations expressed in this material are those of the author(s) and do not necessarily reflect the views of the National Science Foundation.

# References

<div id="refs"></div>

\pagebreak
\appendix
