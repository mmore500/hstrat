from unittest.mock import MagicMock
import warnings

try:
    with warnings.catch_warnings(record=True) as w:
        import Bio.Phylo.TreeConstruction as BioPhyloTree

        if w:
            warnings.warn(
                "ImportWarning: warnings from Biopython import were silenced.",
                ImportWarning,
            )
except:
    warnings.warn(
        "ImportWarning: Bio.Phylo.TreeConstruction import failed; "
        "inserting a no-op mock for BioPhyloTree."
    )
    BioPhyloTree = MagicMock()
