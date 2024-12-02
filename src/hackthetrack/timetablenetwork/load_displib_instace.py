import json
from dataclasses import dataclass
from pathlib import Path
from typing import TypedDict

from hackthetrack.timetablenetwork.components import Resource


@dataclass(frozen=True, slots=True)
class Operation:
    start_lb: float | None
    start_ub: float | None
    min_duration: float
    resources: list[Resource]
    successors: list[int]


class Train(TypedDict):
    id: int
    operations: list[Operation]


class OperationDelayObjective(TypedDict):
    type: str
    train: int
    operation: int
    threshold: float
    increment: float
    coeff: float


@dataclass(frozen=True, slots=True)
class DisplibInstance:
    trains: list[Train]
    objectives: list[OperationDelayObjective]

    @classmethod
    def from_json(cls, path: Path) -> "DisplibInstance":
        return _load_from_displib_format(path)


def _load_from_displib_format(path: Path) -> DisplibInstance:
    with open(path, "r") as file:
        parsed = json.load(file)

    return DisplibInstance(
        trains=[_parse_train(train) for train in parsed["trains"]],
        objectives=[_parse_objectives(obj) for obj in parsed["objective"]],
    )


def _parse_train(data: dict) -> Train:
    """Parse a single train from the DISPLIB format."""
    operations = [
        Operation(
            start_lb=op["start_lb"] if "start_lb" in op else None,
            start_ub=op.get("start_ub") if "start_ub" in op else None,
            min_duration=op["min_duration"],
            resources=[
                Resource(name=res["resource"], release_time=res["release_time"])
                for res in op["resources"]
            ],
            successors=op["successors"],
        )
        for op in data["operations"]
    ]
    return Train(id=data["id"], operations=operations)


def _parse_objectives(data: dict) -> OperationDelayObjective:
    """Parse a single operation delay objective component."""
    if data["type"] != "op_delay":  # They promised to only use this type for now
        raise ValueError(f"Unsupported objective type: {data['type']}")

    return OperationDelayObjective(
        type=data["type"],
        train=data["train"],
        operation=data["operation"],
        threshold=data.get("threshold", 0.0),  # Default to 0 if not present
        increment=data.get("increment", 0.0),  # Default to 0 if not present
        coeff=data.get("coeff", 0.0),  # Default to 0 if not present
    )
