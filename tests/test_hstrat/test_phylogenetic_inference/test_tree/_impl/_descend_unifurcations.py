import dendropy as dp


def descend_unifurcations(node: dp.Node) -> dp.Node:
    while len(node.child_nodes()) == 1:
        node = next(node.child_node_iter())
    return node
