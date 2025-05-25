# Contributing

## Project setup

In case you want to play with the source code or contribute changes, proceed as follows:

1.  Check out the project from GitHub:

    ```bash
    $ git clone https://github.com/roskakori/pygount.git
    $ cd pygount
    ```

2.  Install [uv](https://docs.astral.sh/uv/).

3.  Create the virtual environment and install the required packages:

    ```bash
    $ uv sync --all-groups
    ```

4.  Install the pre-commit hook:

    ```bash
    $ uv run pre-commit install
    ```

## Testing

To run the test suite:

```bash
$ uv run pytest
```

To build and browse the coverage report in HTML format:

```bash
$ sh scripts/test_coverage.sh
$ open htmlcov/index.html  # macOS only
```

## Documentation

To build the documentation in HTML format:

```bash
$ uv run scripts/build_documentation.sh
$ open docs/_build/html/index.html  # macOS only
```

## Coding guidelines

The code throughout uses a natural naming schema avoiding abbreviations, even for local variables and parameters.

Many coding guidelines are automatically enforced (and some even fixed automatically) by the pre-commit hook. If you want to check and clean up the code without performing a commit, run:

```bash
$ uv run pre-commit run --all-files
```

In particular, this applies checks from [black](https://black.readthedocs.io/en/stable/), [flake8](https://flake8.pycqa.org/) and [isort](https://pypi.org/project/isort/).

## Release cheatsheet

This section is only relevant for developers with access to the PyPI project.

To add a new release, first update the `pyproject.toml`:

```toml
[project]
version = "3.x.x"
```

Next, build the project and run the tests to ensure everything works:

```sh
$ rm -rf build  # Remove any files from previous builds.
$ uv build
$ uv run pytest
```

Then create a tag in the repository:

```sh
$ git tag -a -m "Tag version 3.x.x" v3.x.x
$ git push --tags
```

Publish the new version on PyPI:

```sh
$ uv publish
```

Finally, add a GitHub release based on the tag from above to the [release page](https://github.com/roskakori/pygount/releases).
