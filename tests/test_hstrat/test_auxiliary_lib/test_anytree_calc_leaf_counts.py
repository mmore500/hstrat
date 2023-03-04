import anytree

from hstrat._auxiliary_lib import anytree_calc_leaf_counts


def test_anytree_calc_leaf_counts_single_node():
    # Test for a tree with a single node
    root = anytree.Node("A")
    expected_res = {id(root): 1}
    assert anytree_calc_leaf_counts(root) == expected_res


def test_anytree_calc_leaf_counts_multiple_nodes():
    # Example tree structure
    # Node('/A')
    # ├── Node('/A/B')
    # │   ├── Node('/A/B/D')
    # │   └── Node('/A/B/E')
    # └── Node('/A/C')
    #     ├── Node('/A/C/F')
    #     └── Node('/A/C/G')
    #         └── Node('/A/C/G/H')
    root = anytree.Node("A")
    b = anytree.Node("B", parent=root)
    c = anytree.Node("C", parent=root)
    d = anytree.Node("D", parent=b)
    e = anytree.Node("E", parent=b)
    f = anytree.Node("F", parent=c)
    g = anytree.Node("G", parent=c)
    h = anytree.Node("H", parent=g)

    # Test for a tree with multiple nodes
    expected_res = {
        id(root): 4,
        id(b): 2,
        id(c): 2,
        id(d): 1,
        id(e): 1,
        id(f): 1,
        id(g): 1,
        id(h): 1,
    }
    assert anytree_calc_leaf_counts(root) == expected_res
