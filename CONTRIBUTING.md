# Contributing to pygount


## Project setup

In case you want to play with the source code or contribute changes proceed as
follows:

1. Check out the project from GitHub:
   ```bash
   $ git clone https://github.com/roskakori/pygount.git
   $ cd pygount
   ```
2. Create and activate a virtual environment:
   ```bash
   $ python -m venv venv
   $ . venv/bin/activate
   ```
3. Install the required packages:
   ```bash
   $ pip install --upgrade pip
   $ pip install -r dev-requirements.txt
   ```
4. Install the pre-commit hook:
   ```bash
   $ pre-commit install
   ```


## Testing

To run the test suite:
```bash
$ pytest
```

To build and browse the coverage report in HTML format:
```bash
$ pytest --cov-report=html
$ open htmlcov/index.html  # macOS only
```

## Coding guidelines

The code throughout uses a natural naming schema avoiding abbreviations, even
for local variables and parameters.

Many coding guidelines are automatically enforced (and some even fixed
automatically) by the pre-commit hook. If you want to check and clean up
the code without performing a commit, run:
```bash
$ pre-commit run --all-files
```

In particular, this applies [black](https://black.readthedocs.io/en/stable/),
[flake8](https://flake8.pycqa.org/) and
[isort](https://pypi.org/project/isort/).

Other than that
