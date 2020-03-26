# Contributing to pygount

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
   $ pip install --upgrade
   $ pip install -r dev-requirements.txt
   ```
4. Install the pre-commit hook:
   ```bash
   $ pre-commit install
   ```
5. Run the test suite:
   ```bash
   $ pytest
   ```

Use [black](https://black.readthedocs.io/en/stable/) to format the code or
simple wait for the pre-commit hook to fix any formatting issues.
