import os
import sys
import unittest

sys.path.insert(
    0,
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
)

from main import get_test_dependencies


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


if __name__ == "__main__":
    unittest.main()