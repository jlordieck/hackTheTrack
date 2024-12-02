from dataclasses import dataclass
from enum import unique

from ugraph import BaseLinkType, BaseNodeType, LinkABC, NodeABC


@dataclass(frozen=True, slots=True)
class Resource:
    name: str
    release_time: float


@unique
class LinkType(BaseLinkType):
    DEPENDENCY = 1


@dataclass(frozen=True, slots=True)
class Link(LinkABC):
    link_type: LinkType


@unique
class NodeType(BaseNodeType):
    OPERATION = 1


@dataclass(frozen=True, slots=True)
class Node(NodeABC):
    node_type: NodeType
    train_id: int
    lower_bound: float | None
    upper_bound: float | None


@dataclass(frozen=True, slots=True)
class Node(NodeABC):
    index: int
    node_type: NodeType
    train_id: int
    start_lb: float | None
    start_ub: float | None
    min_duration: float
    resources: list[Resource]
    successors: list[int]
