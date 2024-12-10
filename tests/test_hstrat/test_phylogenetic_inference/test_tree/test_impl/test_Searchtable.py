import pytest

from hstrat.phylogenetic_inference.tree._impl import (
    Searchtable,
    SearchtableRecord,
)


@pytest.fixture
def empty_searchtable() -> Searchtable:
    return Searchtable()


@pytest.fixture
def populated_searchtable() -> Searchtable:
    st = Searchtable()
    # Create a simple tree:
    #    0 (root)
    #   / \
    #  1   2 (inner)
    #     / \
    #    3   4
    st.create_offspring(parent_id=0, differentia=None, rank=1, taxon_label="A")
    st.create_offspring(parent_id=0, differentia=102, rank=1, taxon_label="in")
    st.create_offspring(parent_id=2, differentia=None, rank=2, taxon_label="C")
    st.create_offspring(parent_id=2, differentia=None, rank=2, taxon_label="D")
    return st


def test_init(empty_searchtable: Searchtable):
    records = empty_searchtable.to_records()
    assert len(records) == 1
    assert records[0]["taxon_id"] == 0
    assert records[0]["taxon_label"] == "_root"
    assert records[0]["rank"] == 0
    # The root node has itself as search_ancestor_id and search_next_sibling_id
    assert records[0]["search_ancestor_id"] == 0
    assert records[0]["search_next_sibling_id"] == 0
    assert records[0]["search_first_child_id"] == 0


def test_get_differentia_of(populated_searchtable: Searchtable):
    assert populated_searchtable.get_differentia_of(1) is None
    assert populated_searchtable.get_differentia_of(2) == 102


def test_get_rank_of(populated_searchtable: Searchtable):
    assert populated_searchtable.get_rank_of(1) == 1
    assert populated_searchtable.get_rank_of(3) == 2


def test_to_records(populated_searchtable: Searchtable):
    records = populated_searchtable.to_records()
    assert isinstance(records, list)
    assert all(isinstance(r, dict) for r in records)
    node_2 = records[2]
    assert node_2["taxon_id"] == 2
    assert node_2["taxon_label"] == "in"
    assert node_2["differentia"] == 102
    assert node_2["rank"] == 1


def test_has_search_parent(populated_searchtable: Searchtable):
    # The root (0) should have no search parent
    assert not populated_searchtable.has_search_parent(0)
    # All other nodes should have search parents
    for nid in [1, 2, 3, 4]:
        assert populated_searchtable.has_search_parent(nid)


def test_iter_search_children_of(populated_searchtable: Searchtable):
    """Test iterating over search children of a given node."""
    children_of_0 = {*populated_searchtable.iter_search_children_of(0)}
    assert set(children_of_0) == {1, 2}

    children_of_2 = {*populated_searchtable.iter_search_children_of(2)}
    assert set(children_of_2) == {3, 4}

    # Node 3 is a leaf, so no children
    children_of_3 = {*populated_searchtable.iter_search_children_of(3)}
    assert children_of_3 == set()


def test_iter_inner_search_children_of(populated_searchtable: Searchtable):
    """Test iter_inner_search_children_of (excluding leaf nodes)."""
    inner_children_of_0 = {
        *populated_searchtable.iter_inner_search_children_of(0),
    }
    assert inner_children_of_0 == {2}

    inner_children_of_2 = {
        *populated_searchtable.iter_inner_search_children_of(2),
    }
    assert inner_children_of_2 == set()


def test_attach_search_parent(empty_searchtable: Searchtable):
    # Create a node without attaching parent first (directly manipulate records)
    new_taxon_id = len(empty_searchtable._records)
    new_node = SearchtableRecord(
        rank=1,
        taxon_id=new_taxon_id,
        taxon_label="X",
        ancestor_id=0,
        differentia=999,
        search_first_child_id=new_taxon_id,
        search_next_sibling_id=new_taxon_id,
        search_ancestor_id=new_taxon_id,
    )
    empty_searchtable._records.append(new_node)

    # Before attaching
    assert not empty_searchtable.has_search_parent(new_taxon_id)

    # Attach the parent (root: 0)
    empty_searchtable.attach_search_parent(taxon_id=new_taxon_id, parent_id=0)

    # After attaching, should have a parent
    assert empty_searchtable.has_search_parent(new_taxon_id)

    # Check the state with get_records
    records = empty_searchtable.to_records()
    attached_node = records[new_taxon_id]
    assert attached_node["search_ancestor_id"] == 0
    # The parent's first_child should now be new_taxon_id
    assert records[0]["search_first_child_id"] == new_taxon_id
    # The node's next_sibling_id should point to itself if it is the only child
    assert attached_node["search_next_sibling_id"] == new_taxon_id


def test_detach_search_parent(populated_searchtable: Searchtable):
    # Detach node 1 from its parent (0)
    populated_searchtable.detach_search_parent(1)

    # After detachment, node 1 should not have a search parent
    assert not populated_searchtable.has_search_parent(1)

    # Also check that the parent's first_child_id is updated
    records = populated_searchtable.to_records()

    # Previously, 0 had first_child_id as 1 or 2 (depending on insertion order).
    # After detaching 1, the parent's first_child_id should not be 1.
    parent_rec = records[0]
    assert parent_rec["search_first_child_id"] != 1

    # Detached node 1 should have itself as its own ancestor and next_sibling
    detached = records[1]
    assert detached["search_ancestor_id"] == 1
    assert detached["search_next_sibling_id"] == 1


def test_create_offspring(empty_searchtable: Searchtable):
    # Create a single child of root
    cid1 = empty_searchtable.create_offspring(
        parent_id=0, differentia=10, rank=1, taxon_label="Child1"
    )
    records = empty_searchtable.to_records()
    child = records[cid1]
    assert child["ancestor_id"] == 0
    assert child["differentia"] == 10
    assert child["rank"] == 1
    assert child["taxon_label"] == "Child1"
    assert child["search_ancestor_id"] == 0  # after attach_search_parent call
    assert child["search_first_child_id"] == cid1
    assert child["search_next_sibling_id"] == cid1

    # Root should now have a first_child_id equal to the child's ID
    root = records[0]
    assert root["search_first_child_id"] == cid1

    # Create a sibling for the first child
    cid2 = empty_searchtable.create_offspring(
        parent_id=0, differentia=20, rank=1, taxon_label="Child2"
    )
    records = empty_searchtable.to_records()
    root = records[0]
    child1 = records[cid1]
    child2 = records[cid2]

    assert root["search_first_child_id"] == cid2
    assert child2["search_next_sibling_id"] == cid1
    assert child1["search_next_sibling_id"] == cid1
