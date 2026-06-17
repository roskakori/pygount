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

## Spec-driven development

The repository supports spec-driven development based on [spec-kit](https://github.com/github/spec-kit) and [goose]((https://goose-docs.ai/).

To set it up with [homebrew](https://brew.sh/), first install the required tools and LLM models:

```bash
brew install goose-cli ollama specify
ollama pull gemma4:latest  # Model for quick edits.
ollama pull qwen3.6:27b-coding-bf16  # Model for more sophisticated tasks; requires 32 GB VRAM.
```

Next, set up goose:

```bash
goose configure
```

For that:

1. Choose: Configure Providers
2. Choose: Ollama
3. For the next couple of questions use the default.
4. Set the model according to your needs and the abilities of your computer.

Then start goose:

```bash
cd .../pygount
goose
```

## Publish a new version

This section is only relevant for developers with access to the PyPI project.

To add a new release, first update the `pyproject.toml`:

```toml
[project]
version = "3.x.x"
```

Next, build the project and run the tests to ensure everything works:

```sh
$ rm -rf dist  # Remove any files from previous builds.
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
