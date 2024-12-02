from dataclasses import dataclass
from enum import unique

from ugraph import LinkABC, BaseLinkType, BaseNodeType, NodeABC


@unique
class LinkType(BaseLinkType):
    TRAIN = 1


@dataclass(frozen=True, slots=True)
class Link(LinkABC):
    link_type: LinkType
    minimal_duration: float


@unique
class NodeType(BaseNodeType):
    PASSING = 1


@dataclass(frozen=True, slots=True)
class Node(NodeABC):
    node_type: NodeType
    train_id: int
    lower_bound: float | None
    upper_bound: float | None
