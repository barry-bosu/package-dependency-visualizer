import os
import sys
import unittest

sys.path.insert(
    0,
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
)

from main import (
    build_dependency_graph,
    create_test_dependency_getter,
    get_test_dependencies,
)

class TestDependencies(unittest.TestCase):

    def test_direct_dependencies(self):
        dependencies = get_test_dependencies(
            "./test_repository.xml",
            "demo-package",
            "1.0.0",
        )

        self.assertEqual(
            dependencies,
            ["requests", "urllib3", "certifi"],
        )

    def test_package_not_found(self):
        with self.assertRaises(ValueError):
            get_test_dependencies(
                "./test_repository.xml",
                "unknown-package",
                "1.0.0",
            )

    def test_version_not_found(self):
        with self.assertRaises(ValueError):
            get_test_dependencies(
                "./test_repository.xml",
                "demo-package",
                "2.0.0",
            )

    def test_repository_not_found(self):
        with self.assertRaises(ValueError):
            get_test_dependencies(
                "./missing_repository.xml",
                "demo-package",
                "1.0.0",
            )

    def test_transitive_dependency_graph(self):
        getter = create_test_dependency_getter(
            "./test_graph_repository.xml"
        )

        graph = build_dependency_graph(
            "A",
            "1.0.0",
            getter,
        )

        self.assertEqual(graph["A"], ["B", "C"])
        self.assertEqual(graph["B"], ["D"])
        self.assertEqual(graph["C"], ["D"])

    def test_cyclic_dependency_graph(self):
        getter = create_test_dependency_getter(
            "./test_graph_repository.xml"
        )

        graph = build_dependency_graph(
            "A",
            "1.0.0",
            getter,
        )

        self.assertEqual(graph["D"], ["A"])
        self.assertEqual(
            set(graph.keys()),
            {"A", "B", "C", "D"},
        )

    def test_simple_dependency_chain(self):
        getter = create_test_dependency_getter(
            "./test_graph_repository.xml"
        )

        graph = build_dependency_graph(
            "E",
            "1.0.0",
            getter,
        )

        self.assertEqual(
            graph,
            {
                "E": ["F"],
                "F": [],
            },
        )

    def test_package_without_dependencies(self):
        getter = create_test_dependency_getter(
            "./test_graph_repository.xml"
        )

        graph = build_dependency_graph(
            "G",
            "1.0.0",
            getter,
        )

        self.assertEqual(
            graph,
            {
                "G": [],
            },
        )

if __name__ == "__main__":
    unittest.main()