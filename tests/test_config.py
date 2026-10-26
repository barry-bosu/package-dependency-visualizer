import os
import sys
import unittest

sys.path.insert(
    0,
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
)

from main import validate_configuration


class TestConfiguration(unittest.TestCase):

    def create_valid_config(self):
        return {
        "package_name": "demo-package",            "repository": "./test_repository.xml",
        "test_mode": "true",
        "package_version": "1.0.0",
        "output_file": "dependency_graph.png",
    }

    def test_valid_configuration(self):
        valid_config = self.create_valid_config()
        validate_configuration(valid_config)

    def test_empty_package_name(self):
        valid_config = self.create_valid_config()
        valid_config["package_name"] = None
        with self.assertRaises(ValueError):
            validate_configuration(valid_config)

    def test_empty_repository(self):
        valid_config = self.create_valid_config()
        valid_config["repository"] = None
        with self.assertRaises(ValueError):
            validate_configuration(valid_config)

    def test_invalid_test_mode(self):
        valid_config = self.create_valid_config()
        valid_config["test_mode"] = "invalid"
        with self.assertRaises(ValueError):
            validate_configuration(valid_config)

    def test_empty_package_version(self):
        valid_config = self.create_valid_config()
        valid_config["package_version"] = None
        with self.assertRaises(ValueError):
            validate_configuration(valid_config)

    def test_empty_output_file(self):
        valid_config = self.create_valid_config()
        valid_config["output_file"] = None
        with self.assertRaises(ValueError):
            validate_configuration(valid_config)


if __name__ == "__main__":
    unittest.main()