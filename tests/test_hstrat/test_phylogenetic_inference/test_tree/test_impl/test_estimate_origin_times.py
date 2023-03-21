import networkx as nx

import hstrat.phylogenetic_inference.tree._impl as impl


def test_estimate_origin_times_with_simple_tree():
    graph = nx.Graph()
    graph.add_edge("A", "B", length=8)
    graph.add_edge("B", "C", length=2)
    graph.add_edge("C", "D", length=1)
    graph.add_edge("C", "E", length=11)
    leaf_node_origin_times = {"D": 52, "E": 62}

    for node in graph.nodes:
        graph.nodes[node]["taxon_label"] = node

    node_origin_times = impl.estimate_origin_times(
        graph, leaf_node_origin_times
    )
    assert node_origin_times == {
        "E": 62,
        "D": 52,
        "C": 51,
        "B": 49,
        "A": 41,
    }


def test_estimate_origin_times_with_inconsistent_tree():
    graph = nx.Graph()
    graph.add_edge("A", "B", length=8)
    graph.add_edge("B", "C", length=5)
    graph.add_edge("C", "D", length=1)
    graph.add_edge("C", "E", length=10)
    leaf_node_origin_times = {"D": 54, "E": 60}

    for node in graph.nodes:
        graph.nodes[node]["taxon_label"] = node

    node_origin_times = impl.estimate_origin_times(
        graph, leaf_node_origin_times
    )
    for from_, to in graph.edges:
        assert 0 <= node_origin_times[from_] <= node_origin_times[to] <= 60


def test_estimate_origin_times_with_empty_tree():
    graph = nx.Graph()
    leaf_node_origin_times = {}
    node_origin_times = impl.estimate_origin_times(
        graph, leaf_node_origin_times
    )
    assert node_origin_times == {}


def test_estimate_origin_times_with_singleton():
    graph = nx.Graph()
    graph.add_node("Q")
    leaf_node_origin_times = {"Q": 0}
    for node in graph.nodes:
        graph.nodes[node]["taxon_label"] = node

    node_origin_times = impl.estimate_origin_times(
        graph, leaf_node_origin_times
    )
    assert node_origin_times == {"Q": 0}


def test_estimate_origin_times_with_disjoint_tree1():
    graph = nx.Graph()
    graph.add_edge("A", "B", length=8)
    graph.add_edge("B", "C", length=2)
    graph.add_edge("C", "D", length=1)
    graph.add_edge("C", "E", length=11)
    graph.add_node("Q")
    leaf_node_origin_times = {"D": 52, "E": 62, "Q": 17}

    for node in graph.nodes:
        graph.nodes[node]["taxon_label"] = node

    node_origin_times = impl.estimate_origin_times(
        graph, leaf_node_origin_times
    )
    assert node_origin_times == {
        "A": 41,
        "B": 49,
        "C": 51,
        "D": 52,
        "E": 62,
        "Q": 17,
    }


def test_estimate_origin_times_with_disjoint_tree2():
    graph = nx.Graph()
    graph.add_edge("A", "B", length=8)
    graph.add_edge("B", "C", length=2)
    graph.add_edge("C", "D", length=1)
    graph.add_edge("C", "E", length=11)
    graph.add_edge("Q", "R", length=12)
    leaf_node_origin_times = {"D": 52, "E": 62, "Q": 17}

    for node in graph.nodes:
        graph.nodes[node]["taxon_label"] = node

    node_origin_times = impl.estimate_origin_times(
        graph, leaf_node_origin_times
    )
    assert node_origin_times == {
        "A": 41,
        "B": 49,
        "C": 51,
        "D": 52,
        "E": 62,
        "R": 5,
        "Q": 17,
    }
