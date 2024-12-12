from hstrat.phylogenetic_inference.tree._impl import SearchtableRecord


def test_SearchtableRecord_smoke():
    SearchtableRecord(rank=1, taxon_id=1, taxon_label="a")
