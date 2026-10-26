Package Dependency Visualizer is a command-line application for analyzing
package dependencies and generating a dependency graph.

## Stage 1

Stage 1 implements the minimal configurable prototype.

The application reads its configuration from an XML file and displays the
user-configurable parameters in key-value format.

## Configuration

The configuration file is located at:

`config/config.xml`

The following parameters are supported:

- `package_name` - name of the package to analyze.
- `repository` - repository URL or path to a test repository file.
- `test_mode` - enables or disables test repository mode.
- `package_version` - version of the analyzed package.
- `output_file` - name of the generated dependency graph image.

## Running the application

On Windows, run:

`run.bat`

The application can also be started directly with Python:

`python src/main.py`

## Running tests

Run all tests with:

`python -m unittest discover -s tests -v`

## Requirements

- Python 3
- No external Python libraries are required for Stage 1.