## Citing

Please cite hstrat as

bibtex:
```bibtex
@inproceedings{10.1162/isal_a_00550,
  author = {Moreno, Matthew Andres and Dolson, Emily and Ofria, Charles},
  title = "{Hereditary Stratigraphy: Genome Annotations to Enable Phylogenetic Inference over Distributed Populations}",
  volume = {ALIFE 2022: The 2022 Conference on Artificial Life},
  series = {ALIFE 2022: The 2022 Conference on Artificial Life},
  year = {2022},
  month = {07},
  abstract = "{Phylogenies provide direct accounts of the evolutionary trajectories behind evolved artifacts in genetic algorithm and artificial life systems. Phylogenetic analyses can also enable insight into evolutionary and ecological dynamics such as selection pressure and frequency-dependent selection. Traditionally, digital evolution systems have recorded data for phylogenetic analyses through perfect tracking where each birth event is recorded in a centralized data structure. This approach, however, does not easily scale to distributed computing environments where evolutionary individuals may migrate between a large number of disjoint processing elements. To provide for phylogenetic analyses in these environments, we propose an approach to enable phylogenies to be inferred via heritable genetic annotations rather than directly tracked. We introduce a “hereditary stratigraphy” algorithm that enables efficient, accurate phylogenetic reconstruction with tunable, explicit trade-offs between annotation memory footprint and reconstruction accuracy. In particular, we demonstrate an approach that enables estimation of the most recent common ancestor (MRCA) between two individuals with fixed relative accuracy irrespective of lineage depth while only requiring logarithmic annotation space complexity with respect to lineage depth. This approach can estimate, for example, MRCA generation of two genomes within 10\\% relative error with 95\\% confidence up to a depth of a trillion generations with genome annotations smaller than a kilobyte. We also simulate inference over known lineages, recovering up to 85.70\\% of the information contained in the original tree using 64-bit annotations.}",
  booktitle = {Artificial Life Conference Proceedings},
  doi = {10.1162/isal_a_00550},
  url = {https://doi.org/10.1162/isal\_a\_00550},
  note = {64},
  eprint = {https://direct.mit.edu/isal/proceedings-pdf/isal/34/64/2035363/isal\_a\_00550.pdf},
}
```

APA:

> Moreno, M., Dolson, E., & Ofria, C. (2022). Hereditary Stratigraphy: Genome Annotations to Enable Phylogenetic Inference over Distributed Populations. In Artificial Life Conference Proceedings.

Chicago:

> Moreno, Matthew Andres, Emily, Dolson, and Charles, Ofria. "Hereditary Stratigraphy: Genome Annotations to Enable Phylogenetic Inference over Distributed Populations." . In Artificial Life Conference Proceedings. 2022.

MLA:

> Moreno, Matthew Andres et al. "Hereditary Stratigraphy: Genome Annotations to Enable Phylogenetic Inference over Distributed Populations." Artificial Life Conference Proceedings. 2022.

You can also access metadata to cite hstrat in our `CITATION.cff` file [here](https://github.com/mmore500/hstrat/blob/master/CITATION.cff).
Formatted citations were generated via <https://bibtex.online>.
