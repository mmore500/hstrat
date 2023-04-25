import anytree
import pandas as pd

from hstrat._auxiliary_lib import anytree_tree_to_alife_dataframe


def test_singleton():
    original_tree = anytree.Node("beep")
    assert original_tree.name == "beep"
    converted_df = anytree_tree_to_alife_dataframe(original_tree)

    expected_df = pd.DataFrame(
        {
            "id": [0],
            "ancestor_list": ["[None]"],
            "name": ["beep"],
        }
    )

    assert converted_df.equals(expected_df)


def test_simple_tree():
    udo = anytree.Node("Udo", id=0)
    marc = anytree.Node("Marc", parent=udo, id=1111)
    anytree.Node("Lian", parent=marc, id=2222)
    dan = anytree.Node("Dan", parent=udo, id=333)
    anytree.Node("Jet", parent=dan, id=444)
    anytree.Node("Jan", parent=dan, id=555)
    anytree.Node("Joe", parent=dan, id=666)

    converted_df = anytree_tree_to_alife_dataframe(udo)
    expected_df = pd.DataFrame(
        {
            "id": [0, 1111, 333, 2222, 444, 555, 666],
            "ancestor_list": [
                "[None]",
                "[0]",
                "[0]",
                "[1111]",
                "[333]",
                "[333]",
                "[333]",
            ],
            "name": ["Udo", "Marc", "Dan", "Lian", "Jet", "Jan", "Joe"],
        }
    )

    assert converted_df.equals(expected_df)


def test_simple_tree_origin_times():
    udo = anytree.Node("Udo", id=0, edge_length=1)
    marc = anytree.Node("Marc", parent=udo, id=1111, edge_length=1)
    anytree.Node("Lian", parent=marc, id=2222, edge_length=1)
    dan = anytree.Node("Dan", parent=udo, id=333, edge_length=2)
    anytree.Node("Jet", parent=dan, id=444, edge_length=4)
    anytree.Node("Jan", parent=dan, id=555, edge_length=5)
    anytree.Node("Joe", parent=dan, id=666, edge_length=6)

    converted_df = anytree_tree_to_alife_dataframe(udo)
    expected_df = pd.DataFrame(
        {
            "id": [0, 1111, 333, 2222, 444, 555, 666],
            "ancestor_list": [
                "[None]",
                "[0]",
                "[0]",
                "[1111]",
                "[333]",
                "[333]",
                "[333]",
            ],
            "edge_length": [1, 1, 2, 1, 4, 5, 6],
            "name": ["Udo", "Marc", "Dan", "Lian", "Jet", "Jan", "Joe"],
            "origin_time": [1, 2, 3, 3, 7, 8, 9],
        }
    )

    assert converted_df.equals(expected_df)
