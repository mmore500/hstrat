import anytree


def AnyTreeAscendingIter(node: anytree.AnyNode):
    while node is not None:
        yield node
        node = node.parent
