from typing import NamedTuple, NewType
import gurobipy as grb
from hackthetrack.dependencygraph import DependencyGraph


TrainId = NewType("TrainId", int)
EventId = NewType("EventId", int)
NextEventId = NewType("NextEventId", int)

class DisplibParameters:
    pass


class DisplibData(NamedTuple):
    parameters: DisplibParameters
    network: DependencyGraph


class _DisplibVariables(NamedTuple):
    time_variables: grb.tupledict[TrainId, EventId, grb.Var]
    route_variables: grb.tupledict[TrainId, EventId, grb.Var]
    consecutive_events_variables: grb.tupledict[TrainId, EventId, NextEventId, grb.Var]





@dataclass  # (frozen=True)
class DISPLIB:
    _model: grb.Model
    _variables: _DisplibVariables
    _data: DisplibData

    def solve(self, write_lp: bool = False, lp_file_path: Optional[str] = None) -> None:
        if write_lp:
            if not lp_file_path:
                lp_file_path = f"{self.__class__.__name__}.lp"
            self._model.write(lp_file_path)

        self._model.optimize()

def create_displib_mip(displib_data: DisplibData) -> DISPLIB:
    _add_constraints(displib_data, displib_model := grb.Model(), displib_variables := _add_variables(displib_model, displib_data))
    return DISPLIB(displib_model, displib_variables, displib_data)


def build_mip_from_dependency_graph(network: DependencyGraph) -> None:
    displib_mip = create_displib_mip(planning_data)
    displib_mip.solve(write_lp=True)

def _add_constraints(displib_data: DisplibData, displib_model: grb.Model, displib_variables: _DisplibVariables) -> None:
    pass


def _add_time_variables(displib_model, displib_data) -> grb.tupledict[TrainId, EventId, grb.Var]:
    time_variables = grb.tupledict(TrainId, EventId, grb.Var)
    nodes = displib_data.network.all_nodes
    for node in nodes:
        time_variables[node.train_id, node.id] = displib_model.addVar(
            lb=node.start_lb,
            ub=node.start_ub,
            name=f"t_{node.id}")




def _add_variables(displib_model: grb.Model, displib_data: DisplibData) -> _DisplibVariables:
    _add_time_variables(displib_model, displib_data)