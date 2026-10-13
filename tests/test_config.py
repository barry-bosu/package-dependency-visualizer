import os
import sys
import unittest

sys.path.insert(
    0,
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
)

from main import validate_configuration


class TestConfiguration(unittest.TestCase):

    def setUp(self):
        self.valid_config = {
            "package_name": "demo-package",
            "repository": "./test_repository.xml",
            "test_mode": "true",
            "package_version": "1.0.0",
            "output_file": "dependency_graph.png",
        }

    def test_valid_configuration(self):
        validate_configuration(self.valid_config)

    def test_empty_package_name(self):
        self.valid_config["package_name"] = None
        with self.assertRaises(ValueError):
            validate_configuration(self.valid_config)

    def test_empty_repository(self):
        self.valid_config["repository"] = None
        with self.assertRaises(ValueError):
            validate_configuration(self.valid_config)

    def test_invalid_test_mode(self):
        self.valid_config["test_mode"] = "invalid"
        with self.assertRaises(ValueError):
            validate_configuration(self.valid_config)

    def test_empty_package_version(self):
        self.valid_config["package_version"] = None
        with self.assertRaises(ValueError):
            validate_configuration(self.valid_config)

    def test_empty_output_file(self):
        self.valid_config["output_file"] = None
        with self.assertRaises(ValueError):
            validate_configuration(self.valid_config)


if __name__ == "__main__":
    unittest.main()