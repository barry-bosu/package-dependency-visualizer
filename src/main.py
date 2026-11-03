import json
import subprocess
import sys
import urllib.error
import urllib.request
import xml.etree.ElementTree as element_tree


def load_configuration(config_path):
    try:
        tree = element_tree.parse(config_path)
        root = tree.getroot()
    except FileNotFoundError:
        raise ValueError(
            f"Configuration file not found: {config_path}"
        )
    except element_tree.ParseError:
        raise ValueError(
            "Configuration file contains invalid XML"
        )

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


def get_test_dependencies(
    repository_path,
    package_name,
    package_version,
):
    """Return direct dependencies from the test repository."""
    try:
        tree = element_tree.parse(repository_path)
        root = tree.getroot()
    except FileNotFoundError:
        raise ValueError(
            f"Repository file not found: {repository_path}"
        )
    except element_tree.ParseError:
        raise ValueError(
            "Repository file contains invalid XML"
        )

    for package in root.findall("package"):
        if (
            package.get("name") == package_name
            and package.get("version") == package_version
        ):
            return [
                dependency.text
                for dependency in package.findall(
                    "./dependencies/dependency"
                )
            ]

    raise ValueError(
        f"Package {package_name} version "
        f"{package_version} not found"
    )


def get_repository_dependencies(
    repository_url,
    package_name,
    package_version,
):
    """Return dependencies from a Python package repository."""
    repository_url = repository_url.rstrip("/")
    package_url = (
        f"{repository_url}/{package_name}/"
        f"{package_version}/json"
    )

    try:
        with urllib.request.urlopen(package_url) as response:
            package_data = json.load(response)
    except urllib.error.HTTPError as error:
        raise ValueError(
            f"Package {package_name} version "
            f"{package_version} not found"
        ) from error
    except urllib.error.URLError as error:
        raise ValueError(
            f"Cannot connect to repository: {repository_url}"
        ) from error

    return package_data["info"].get("requires_dist") or []


def build_dependency_graph(
    package_name,
    package_version,
    get_dependencies,
):
    """Build the dependency graph using iterative DFS."""
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
                stack.append(
                    (dependency, current_version)
                )

    return graph


def get_reverse_dependencies(graph, package_name):
    """Return packages that depend on the specified package."""
    reverse_dependencies = []

    for package, dependencies in graph.items():
        if package_name in dependencies:
            reverse_dependencies.append(package)

    return reverse_dependencies


def generate_graphviz(graph):
    """Generate a Graphviz DOT representation."""
    lines = ["digraph dependencies {"]

    for package, dependencies in graph.items():
        if not dependencies:
            lines.append(f'    "{package}";')

        for dependency in dependencies:
            lines.append(
                f'    "{package}" -> "{dependency}";'
            )

    lines.append("}")
    return "\n".join(lines)


def save_graph_image(graphviz_text, output_file):
    """Save a Graphviz graph as a PNG image."""
    process = subprocess.run(
        ["dot", "-Tpng", "-o", output_file],
        input=graphviz_text,
        text=True,
        capture_output=True,
        check=False,
    )

    if process.returncode != 0:
        raise ValueError(
            f"Graphviz error: {process.stderr.strip()}"
        )


def create_test_dependency_getter(repository_path):
    """Create a dependency getter for the test repository."""

    def get_dependencies(package_name, package_version):
        return get_test_dependencies(
            repository_path,
            package_name,
            package_version,
        )

    return get_dependencies


def visualize_test_package(
    repository_path,
    package_name,
    package_version,
    output_file,
):
    """Build and visualize one test package graph."""
    dependency_getter = create_test_dependency_getter(
        repository_path
    )

    graph = build_dependency_graph(
        package_name,
        package_version,
        dependency_getter,
    )

    graphviz_text = generate_graphviz(graph)

    print(
        f"\nGraphviz for package {package_name}:"
    )
    print(graphviz_text)

    save_graph_image(
        graphviz_text,
        output_file,
    )

    print(f"Graph saved to {output_file}")


def demonstrate_visualizations(repository_path):
    """Create visualizations for three test packages."""
    examples = [
        ("A", "graph_A.png"),
        ("E", "graph_E.png"),
        ("G", "graph_G.png"),
    ]

    for package_name, output_file in examples:
        visualize_test_package(
            repository_path,
            package_name,
            "1.0.0",
            output_file,
        )


def main():
    config_path = "config/config.xml"

    try:
        config = load_configuration(config_path)
        validate_configuration(config)

        if config["test_mode"] == "true":
            visualize_test_package(
                config["repository"],
                config["package_name"],
                config["package_version"],
                config["output_file"],
            )

            demonstrate_visualizations(
                config["repository"]
            )

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