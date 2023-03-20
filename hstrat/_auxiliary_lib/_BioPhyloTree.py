from unittest.mock import MagicMock
import warnings

try:
    with warnings.catch_warnings(record=True) as w:
        import Bio.Phylo.TreeConstruction as BioPhyloTree

        _ = BioPhyloTree

        if w:  # pragma: no cover
            warnings.warn(
                "ImportWarning: warnings from Biopython import were silenced.",
                ImportWarning,
            )
except:  # pragma: no cover
    warnings.warn(
        "ImportWarning: Bio.Phylo.TreeConstruction import failed; "
        "inserting a no-op mock for BioPhyloTree."
    )
    BioPhyloTree = MagicMock()
