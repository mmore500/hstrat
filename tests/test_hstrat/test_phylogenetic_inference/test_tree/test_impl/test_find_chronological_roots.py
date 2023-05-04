import networkx as nx

import hstrat.phylogenetic_inference.tree._impl as impl


def test_find_chronological_root_with_simple_tree():
    graph = nx.Graph()
    graph.add_edge("A", "B", length=8)
    graph.add_edge("B", "C", length=2)
    graph.add_edge("C", "D", length=1)
    graph.add_edge("C", "E", length=11)
    leaf_node_origin_times = {"D": 52, "E": 62}

    for node in graph.nodes:
        graph.nodes[node]["taxon_label"] = node

    root = impl.find_chronological_roots(graph, leaf_node_origin_times)
    assert root == ["A"]


def test_find_chronological_root_with_empty_tree():
    graph = nx.Graph()
    leaf_node_origin_times = {}
    roots = impl.find_chronological_roots(graph, leaf_node_origin_times)
    assert roots == []


def test_find_chronological_root_with_singleton():
    graph = nx.Graph()
    graph.add_node("Q")
    leaf_node_origin_times = {"Q": 0}
    for node in graph.nodes:
        graph.nodes[node]["taxon_label"] = node

    roots = impl.find_chronological_roots(graph, leaf_node_origin_times)
    assert roots == ["Q"]


def test_find_chronological_root_with_disjoint_tree1():
    graph = nx.Graph()
    graph.add_edge("A", "B", length=8)
    graph.add_edge("B", "C", length=2)
    graph.add_edge("C", "D", length=1)
    graph.add_edge("C", "E", length=11)
    graph.add_node("Q")
    leaf_node_origin_times = {"D": 52, "E": 62, "Q": 17}

    for node in graph.nodes:
        graph.nodes[node]["taxon_label"] = node

    root = impl.find_chronological_roots(graph, leaf_node_origin_times)
    assert root == ["A", "Q"]


def test_find_chronological_root_with_disjoint_tree2():
    graph = nx.Graph()
    graph.add_edge("A", "B", length=8)
    graph.add_edge("B", "C", length=2)
    graph.add_edge("C", "D", length=1)
    graph.add_edge("C", "E", length=11)
    graph.add_edge("Q", "R", length=12)
    leaf_node_origin_times = {"D": 52, "E": 62, "Q": 17}

    for node in graph.nodes:
        graph.nodes[node]["taxon_label"] = node

    root = impl.find_chronological_roots(graph, leaf_node_origin_times)
    assert root == ["A", "R"]
