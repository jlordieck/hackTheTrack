from ugraph import EndNodeIdPair, MutableNetworkABC, NodeId, ThreeDCoordinates

from hackthetrack.dependencygraph.components import Link, LinkType, Node, NodeType
from hackthetrack.displib.load_displib_instance import DisplibInstance


class DependencyGraph(MutableNetworkABC[Node, Link, NodeType, LinkType]):

    @classmethod
    def from_displib_instance(cls, instance: DisplibInstance) -> "DependencyGraph":
        return _create_dependency_graph(instance)

    def node_by_train_id_and_index(self, train_id: int, index: int) -> Node:
        return self.node_by_id(NodeId(f"train_{train_id}_op_{index}"))


def _create_dependency_graph(instance: DisplibInstance) -> DependencyGraph:
    """Create a timetable network from a DisplibInstance."""
    network = DependencyGraph.create_empty()
    node_ids_per_train: list[list[NodeId]] = [[] for _ in instance.trains]
    nodes_to_add = []
    for train in instance.trains:
        for op_idx, operation in enumerate(train["operations"]):
            node_id = NodeId(f"train_{train['id']}_op_{op_idx}")
            node = Node(
                index=operation.index,
                id=node_id,
                coordinates=ThreeDCoordinates(x=0, y=0, z=0),  # FIXME: Here we could most like do better
                node_type=NodeType.OPERATION,
                train_id=train["id"],
                start_lb=operation.start_lb,
                start_ub=operation.start_ub,
                min_duration=operation.min_duration,
                resources=operation.resources,
                successors=operation.successors,
            )
            nodes_to_add.append(node)
            node_ids_per_train[train["id"]].append(node_id)
    network.add_nodes(nodes_to_add)

    links_to_add = []
    for train in instance.trains:
        train_id = train["id"]
        for op_idx, operation in enumerate(train["operations"]):
            s_id = node_ids_per_train[train_id][op_idx]
            for successor_idx in operation.successors:
                s_t = EndNodeIdPair((s_id, node_ids_per_train[train_id][successor_idx]))
                links_to_add.append((s_t, Link(link_type=LinkType.DEPENDENCY)))
    network.add_links(links_to_add)
    return network
