from pathlib import Path
import hexaly.optimizer

from hackthetrack.dependencygraph.network import DependencyGraph
from hackthetrack.displib.load_displib_instance import DisplibInstance

displib_instance_path = Path("out/instances/displib_instances_phase1/line1_critical_0.json")
instance = DisplibInstance.from_json(displib_instance_path)
network = DependencyGraph.from_displib_instance(instance)

operations = [node.index for node in network.all_nodes]
num_operations = len(network.all_nodes)

with hexaly.optimizer.HexalyOptimizer() as optimizer:
    model = optimizer.get_model()

    operations = [model.interval(0, horizon) for _ in range(num_operations)]
    operation_array = model.array(operations)

    resource_allocation = model.array([model.list(num_operations) for _ in range(num_resources)])

    operation_to_train_array = model.array(operation_to_train)

    # lower bound on operation duration
    for operation, duration in zip(operations, durations):
        model.add_constraint(model.length(operation) >= duration)

    # ordering of operations on the same resource with release times if subsequent operations are on different trains
    for r in range(num_resources):
        sequence = resource_allocation[r]
        release_times_for_resource = model.array(release_times[r])
        sequence_lambda = model.lambda_function(
            lambda i: operation_array[sequence[i]]
            + (operation_to_train_array[sequence[i]] != operation_to_train_array[sequence[i + 1]])
            * release_times_for_resource[sequence[i]]
            < operation_array[sequence[i + 1]]
        )
        model.constraint(model.and_(model.range(0, model.count(sequence) - 1), sequence_lambda))

    # no-wait and routing of trains
    for node in network.all_nodes:
        neighbors = network.neighbors(node.id, "out")
        if len(neighbors) == 0:
            continue
        elif len(neighbors) == 1:
            model.add_constraint(
                model.end(operation_array[node.index]) == model.start(operation_array[neighbors[0].index])
            )
        else:
            model.add_constraint(
                model.or_(
                    [
                        model.end(operation_array[node.index]) == model.start(operation_array[neighbor.index])
                        for neighbor in neighbors
                    ]
                )
            )
