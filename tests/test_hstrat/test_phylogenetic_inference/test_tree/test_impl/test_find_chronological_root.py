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

    root = impl.find_chronological_root(graph, leaf_node_origin_times)
    assert root == "A"
