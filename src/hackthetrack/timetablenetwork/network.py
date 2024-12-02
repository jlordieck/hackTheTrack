from ugraph import MutableNetworkABC

from hackthetrack.timetablenetwork.components import NodeType, Link, Node, LinkType


class TimeTableNetwork(MutableNetworkABC[Node, Link, NodeType, LinkType]):
    pass
