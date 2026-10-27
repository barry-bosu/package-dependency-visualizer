import json
import sys
import urllib.error
import urllib.request
import xml.etree.ElementTree as element_tree

def load_configuration(config_path):
    try:
        tree = element_tree.parse(config_path)
        root = tree.getroot()
    except FileNotFoundError:
        raise ValueError(f"Configuration file not found: {config_path}")
    except element_tree.ParseError:
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

def get_test_dependencies(repository_path, package_name, package_version):
    """Return direct dependencies from the test repository."""
    try:
        tree = element_tree.parse(repository_path)
        root = tree.getroot()
    except FileNotFoundError:
        raise ValueError(f"Repository file not found: {repository_path}")
    except element_tree.ParseError:
        raise ValueError("Repository file contains invalid XML")

    for package in root.findall("package"):
        if (
            package.get("name") == package_name
            and package.get("version") == package_version
        ):
            return [
                dependency.text
                for dependency in package.findall("./dependencies/dependency")
            ]

    raise ValueError(
        f"Package {package_name} version {package_version} not found"
    )

def get_repository_dependencies(repository_url, package_name, package_version):
    repository_url = repository_url.rstrip("/")
    package_url = (
        f"{repository_url}/{package_name}/{package_version}/json"
    )

    try:
        with urllib.request.urlopen(package_url) as response:
            package_data = json.load(response)
    except urllib.error.HTTPError as error:
        raise ValueError(
            f"Package {package_name} version {package_version} not found"
        ) from error
    except urllib.error.URLError as error:
        raise ValueError(
            f"Cannot connect to repository: {repository_url}"
        ) from error

    return package_data["info"].get("requires_dist") or []

#esto es de la tercera fase
def build_dependency_graph(
    package_name,
    package_version,
    get_dependencies,
):
    graph = {}
    visited = set()
    stack = [(package_name, package_version)]

    while stack:
        current_package, current_version = stack.pop()

        if current_package in visited:
            continue

        visited.add(current_package)

        dependencies = get_dependencies(
            current_package,
            current_version,
        )

        graph[current_package] = dependencies

        for dependency in reversed(dependencies):
            if dependency not in visited:
                stack.append((dependency, current_version))

    return graph

def create_test_dependency_getter(repository_path):
    def get_dependencies(package_name, package_version):
        return get_test_dependencies(
            repository_path,
            package_name,
            package_version,
        )

    return get_dependencies

def main():
    config_path = "config/config.xml"

    try:
        config = load_configuration(config_path)
        validate_configuration(config)

        if config["test_mode"] == "true":
            dependency_getter = create_test_dependency_getter(
                config["repository"]
            )

            graph = build_dependency_graph(
                config["package_name"],
                config["package_version"],
                dependency_getter,
            )

            for package, dependencies in graph.items():
                print(f"{package}: {', '.join(dependencies)}")
        else:
            dependencies = get_repository_dependencies(
                config["repository"],
                config["package_name"],
                config["package_version"],
            )

            for dependency in dependencies:
                print(dependency)

    except ValueError as error:
        print(f"Error: {error}")
        sys.exit(1)

if __name__ == "__main__":
    main()