Usage
=====

General
-------

Simply run and specify the folder to analyze recursively, for example:

.. code-block:: bash

    $ pygount ~/development/sometool

If you omit the folder, the current folder of your shell is used as starting
point. Apart from folders you can also specify single files and shell patterns
(using ``?``, ``*`` and ranges like ``[a-z]``).

Certain files and folders are automatically excluded from the analysis:

* files starting with dot (``.``) or ending in tilda (``~``)
* folders starting with dot (``.``) or named ``_svn``.

To specify alternative patterns, use ``--folders-to-skip`` and
``--names-to-skip``. Both take a comma separated list of patterns, see below
on the pattern syntax. To for example also prevent folders starting with two
underscores (``_``) from being analyzed, specify
``--folders-to-skip=[...],__*``.

To limit the analysis on certain file types, you can specify a comma separated
list of suffixes to take into account, for example ``--suffix=py,sql,xml``.

By default the result of the analysis are written to the standard output in a
format similar to sloccount. To redirect the output to a file, use e.g.
``--out=counts.txt``. To change the format to an XML file similar to cloc, use
``--format=cloc-xml``.

To just get a quick grasp of the languages used in a project and their
respective importance use ``--format=summary`` which provides a language
overview and a sum total. For example pygount's summary looks like this::

    Language      Code    %     Comment    %
    ----------------  ----  ------  -------  ------
    Python            1730   83.94      250   78.12
    reStructuredText   271   13.15        0    0.00
    Ant                 38    1.84        1    0.31
    INI                 10    0.49        1    0.31
    Bash                 8    0.39        2    0.62
    TOML                 4    0.19        0    0.00
    Text                 0    0.00       66   20.62
    ----------------  ----  ------  -------  ------
    Sum total         2061              320

The summary output is designed for human readers and the column widths adjust
to the data.


Patterns
--------

Some command line arguments take patterns as values.

By default, patterns are shell patterns using ``*``, ``?`` and ranges like
``[a-z]`` as placeholders. Depending on your platform, the are case sensitive
(Unix) or not (Mac OS, Windows).

If a pattern starts with ``[regex]`` you can specify a comma separated list
of regular expressions instead using all the constructs supported by the
`Python regular expression syntax <https://docs.python.org/3/library/re.html#regular-expression-syntax>`_.
Regular expressions are case sensitive unless they include a ``(?i)`` flag.

If the first actual pattern is ``[...]``, default patterns are included.
Without it, defaults are ignored and only the pattern explicitly stated are
taken into account.

So for example to specify that generated code can also contain the German word
"generiert" in a case insensivie way use
``--generated="[regex][...](?i).*generiert"``.


Source code encoding
----------------------

When reading source code, pygount automatically detects the encoding. It uses
a simple algorithm where it recognizes BOM, XML declarations such as:

.. code-block:: xml

    <?xml encoding='cp1252'?>

and "magic" comments such as:

.. code-block:: python

    # -*- coding: cp1252 -*-

If the file does not have an appropriate heading, pygount attempts to read it
using UTF-8. If this fails, it reads the file using a fallback encoding (by
default CP1252) and ignores any encoding errors.

You can change this behavior using the ``--encoding`` option:

* To keep the automatic analysis and use a different fallback encoding specify
  for example ``--encoding=automatic;iso-8859-15``.
* To use an automatic detection based on heuristic, use
  ``--encoding=chardet``. For this to work, the
  `chardet <https://pypi.python.org/pypi/chardet>`_ package must be installed,
* To use a specific encoding (for all files analyzed), use for example
  ``--encoding=iso-8859-15``.


Pseudo languages
----------------

If a source code is not counted, the number of lines is 0 and the language
shown is a pseudo language indicating the reason:

* ``__binary__`` - the source code is a binary file; the detection of binary files
  first ensures that file does not start with a BOM for UTF-8, UTF-16 or
  UTF-32 (which indicates text files). After that it checks for zero bytes
  within the initial 8192 bytes of the file.
* ``__duplicate__`` - the source code is a bytewise identical copy of another
  file; enable the command line option ``--duplicates`` to also count code in
  duplicates (and gain a minor performance improvement).
* ``__empty__`` - the source code is an empty file with a size of 0 bytes.
* ``__error__`` - the source code could not be parsed e.g. due to an I/O error.
* ``__generated__`` - the source code is generated according to the command line
  option ``--generated``.
* ``__unknown__`` - pygments does not provide a lexer to parse the source code.


## Other information

To get a description of all the available command line options, run:

.. code-block:: bash

    $ pygount --help

To get the version number, run:

.. code-block:: bash

    $ pygount --version