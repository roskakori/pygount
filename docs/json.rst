JSON
####

The JavaScript objects notation (JSON) is widely used to interchange data.
Running pygount with :option:`--format` "json" is a simple way to provide
the results of an analysis for further processing.


General format
==============

The general structure of the resulting JSON is:

.. code-block:: JavaScript

  {
    "formatVersion": "1.1.0",
    "pygountVersion": "1.8.0",
    "files": [...],
    "languages": [...],
    "runtime": {...},
    "summary": {...}
  }

The naming of the entries deliberately uses camel case to conform to the
`JSLint <https://www.jslint.com/>`_ guidelines.

Both ``formatVersion`` and ``pygountVersion`` use
`semantic versioning <https://semver.org/>`_. For more information about how
this JSON evolved, see :ref:`JSON format history`.

Files
-----

With ``files`` you can access a list of files analyzed, for example:

.. code-block:: JavaScript

  {
    "codeCount": 171,
    "documentationCount": 28,
    "emptyCount": 56,
    "group": "pygount",
    "isCountable": true,
    "language": "Python",
    "lineCount": 266,
    "path": "/tmp/pygount/pygount/write.py",
    "state": "analyzed",
    "stateInfo": null,
    "sourceCount": 182
  }

The ``*Count`` fields have the following meaning:

* ``codeCount``: The number of lines that contains code, excluding
  :ref:?`Pure string lines`
* ``documentationCount``: The number of lines containing comments
* ``emptyCount``: The number of empty lines,  which includes
  ":ref:`No operations`" lines
* ``lineCount``: Basically the number of lines shown in your editor
  respectively computed by shell commands like ``wc -l``,
* ``sourceCount``: The source lines of code, similar to the traditional SLOC
* ``stringCount``: The number of :ref:`Pure string lines`

Here, ``sourceCount`` is the number of source lines of code (SLOC),
``documentationCount`` the number of lines containing comments and

The ``state`` can have one of the following values:

* analyzed: successfully analyzed
* binary: the file is a  :ref:`binary file <binary>`
* duplicate: the file is a :ref:`duplicate <duplicates>` of another
* empty: the file is empty (file size = 0)
* error: the source could not be parsed; in this case, ``stateInfo``
  contains a message with more details
* generated: the file has been generated as specified with :option:`--generated`
* unknown: pygments does not offer any lexer to analyze the file

Languages
---------

In ``languages`` the summary for each language is available, for example:

.. code-block:: JavaScript

  {
    "documentationCount": 429,
    "documentationPercentage": 11.776008783969257,
    "codeCount": 2332,
    "codePercentage": 64.01317595388416,
    "emptyCount": 706,
    "emptyPercentage": 19.3796321712874,
    "fileCount": 20,
    "filePercentage": 48.78048780487805,
    "isPseudoLanguage": false,
    "language": "Python",
    "sourceCount": 2508,
    "sourcePercentage": 68.84435904474334,
    "stringCount": 176,
    "stringPercentage": 4.831183090859182
  }


Summary
-------

In ``summary`` the total counts across the whole project can be accessed, for
example:

.. code-block:: JavaScript

  "summary": {
    "totalCodeCount": 4366,
    "totalCodePercentage": 68.38972431077694,
    "totalDocumentationCount": 463,
    "totalDocumentationPercentage": 7.25250626566416,
    "totalEmptyCount": 1275,
    "totalEmptyPercentage": 19.971804511278197,
    "totalFileCount": 41,
    "totalSourceCount": 4646,
    "totalSourcePercentage": 72.77568922305764,
    "totalStringCount": 280,
    "totalStringPercentage": 4.385964912280702
  }

Runtime
-------

The ``runtime`` entry collects general information about how well pygount performed
in collecting the information, for example:

.. code-block:: JavaScript

  "runtime": {
    "durationInSeconds": 0.6333059999999999,
    "filesPerSecond": 64.73963613166464,
    "finishedAt": "2024-05-13T16:14:31.977070+00:00",
    "linesPerSecond": 10080.435050354807,
    "startedAt": "2024-05-13T16:14:31.343764+00:00"
  }

Pretty printing
===============

Because the output is concise and consequently mostly illegible for a
human reader, you might want to pipe it through a pretty printer. As you
already have python installed, the easiest way is:

.. code-block:: sh

  pygount --format json | python -m json.tool

Another alternativ would be `jq <https://stedolan.github.io/jq/>`_:

.. code-block:: sh

  pygount --format json | jq .

.. _JSON format history:

JSON format history
===================

v1.1.0, pygount 1.8.0

* Add ``code_count`` and ``line_count``

v1.0.0, pygount 1.3.0

* Initial version
