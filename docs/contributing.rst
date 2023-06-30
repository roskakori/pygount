Contributing
############

Project setup
-------------

In case you want to play with the source code or contribute changes proceed as
follows:

1. Check out the project from GitHub:

   .. code-block:: bash

       $ git clone https://github.com/roskakori/pygount.git
       $ cd pygount

2. Install `poetry <https://python-poetry.org/>`_.

3. Create the virtual environment and install the required packages:

   .. code-block:: bash

       $ poetry install

4. Install the pre-commit hook:

   .. code-block:: bash

       $ poetry run pre-commit install


Testing
-------

To run the test suite:

.. code-block:: bash

    $ poetry run pytest

To build and browse the coverage report in HTML format:

.. code-block:: bash

    $ sh scripts/test_coverage.sh
    $ open htmlcov/index.html  # macOS only


Documentation
-------------

To build the documentation in HTML format:

.. code-block:: bash

    $ poetry run scripts/build_documentation.sh
    $ open docs/_build/html/index.html  # macOS only


Coding guidelines
-----------------

The code throughout uses a natural naming schema avoiding abbreviations, even
for local variables and parameters.

Many coding guidelines are automatically enforced (and some even fixed
automatically) by the pre-commit hook. If you want to check and clean up
the code without performing a commit, run:

.. code-block:: bash

    $ poetry run pre-commit run --all-files

In particular, this applies `black <https://black.readthedocs.io/en/stable/>`_,
`flake8 <https://flake8.pycqa.org/>`_ and
`isort <https://pypi.org/project/isort/>`_.

Release cheatsheet
------------------

This section only relevant for developers with access to the PyPI project.

To add a new release, first update the :file:`pyproject.toml`:

.. code-block:: toml

    [tool.poetry]
    version = "1.x.x"

Next build the project and run the tests to ensure everything works:

.. code-block:: sh

    $ poetry build
    $ poetry run pytest

Then create a tag in the repository:

.. code-block:: sh

    $ git tag -a -m "Tag version 1.x.x" v1.x.x
    $ git push --tags

Publish the new version on PyPI:

.. code-block:: sh

    $ poetry publish

Finally, add a release based on the tag from above to the
`release page <https://github.com/roskakori/pygount/releases>`_.
