import unittest
from pathlib import Path

from hackthetrack.dependencygraph import DependencyGraph
from hackthetrack.displib import DisplibInstance


class TestGraphCreation(unittest.TestCase):

    def set_up(self) -> None:
        pass  # check later if file exists (othwerwise the test will fail)

    def test_graph_creation(self) -> None:
        path = Path("src/hackthetrack_tests/dependencygraph_test/data/displib_testinstances_headway1.json")
        network = DependencyGraph.from_displib_instance(DisplibInstance.from_json(path))
        self.assertEqual(network.n_count, 8)
        self.assertEqual(network.l_count, 6)
