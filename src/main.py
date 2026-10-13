import sys
import xml.etree.ElementTree as ET


def load_configuration(config_path):
    try:
        tree = ET.parse(config_path)
        root = tree.getroot()
    except FileNotFoundError:
        raise ValueError(f"Configuration file not found: {config_path}")
    except ET.ParseError:
        raise ValueError("Configuration file contains invalid XML")

    return {
        "package_name": root.findtext("package_name"),
        "repository": root.findtext("repository"),
        "test_mode": root.findtext("test_mode"),
        "package_version": root.findtext("package_version"),
        "output_file": root.findtext("output_file"),
    }

def validate_configuration(config):
    if not config["package_name"]:
        raise ValueError("package_name cannot be empty")

    if not config["repository"]:
        raise ValueError("repository cannot be empty")

    if config["test_mode"] not in ("true", "false"):
        raise ValueError("test_mode must be true or false")

    if not config["package_version"]:
        raise ValueError("package_version cannot be empty")

    if not config["output_file"]:
        raise ValueError("output_file cannot be empty")

def print_configuration(config):
    for key, value in config.items():
        print(f"{key}={value}")


def main():
    config_path = "config/config.xml"

    try:
        config = load_configuration(config_path)
        validate_configuration(config)
        print_configuration(config)
    except ValueError as error:
        print(f"Error: {error}")
        sys.exit(1)


if __name__ == "__main__":
    main()