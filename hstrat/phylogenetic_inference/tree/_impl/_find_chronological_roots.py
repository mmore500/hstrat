import numbers
import statistics
import typing

from iterpop import iterpop as ip
import networkx as nx
import sortedcontainers as sc

from ._estimate_origin_times import estimate_origin_times


def find_chronological_roots(
    graph: nx.Graph,
    leaf_node_depths: typing.Dict[str, numbers.Number],
) -> typing.List[str]:
    """Work backward from known phylogenetic depths of leaf nodes to identify
    a likely most ancient ancestor."""

    node_origin_times = estimate_origin_times(graph, leaf_node_depths)

    # extract root node of each connected component
    root_nodes = [
        min(component, key=lambda node: node_origin_times[node])
        for component in nx.connected_components(graph)
    ]

    return [graph.nodes[root_node]["taxon_label"] for root_node in root_nodes]