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
    PRECEDENCE = 2


@dataclass(frozen=True, slots=True)
class Link(LinkABC):
    pass


@unique
class NodeType(BaseNodeType):
    OPERATION = 1
    RESOURCE = 2


@dataclass(frozen=True, slots=True)
class Node(NodeABC):
    index: int
    train_id: int
    start_lb: float | None
    start_ub: float | None
    min_duration: float
    resources: list[Resource]
    successors: list[int]
