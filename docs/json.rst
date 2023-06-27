JSON
####

.. program:: pygount

The JavaScript objects notation (JSON) is widely used to interchange data.
Running pygount with :option:`--format` "json" is a simple way to provide
the results of an analysis for further processing.


General format
--------------

The general structure of the resulting JSON is:

.. code-block:: JavaScript

  {
    "formatVersion": "1.0.0",
    "pygountVersion": "1.3.0",
    "files": [...],
    "languages": [...],
    "runtime": {...},
    "summary": {...}
  }

The naming of the entries deliberately uses camel case to conform to the
`JSLint <https://www.jslint.com/>`_ guidelines.

Both ``formatVersion`` and ``pygountVersion`` use
`semantic versioning <https://semver.org/>`_. The other entries contain the following information:

With ``files`` you can access a list of files analyzed, for example:

.. code-block:: JavaScript

  {
    "path": "/Users/someone/workspace/pygount/pygount/write.py",
    "sourceCount": 253,
    "emptyCount": 60,
    "documentationCount": 27,
    "group": "pygount",
    "isCountable": true,
    "language": "Python",
    "state": "analyzed",
    "stateInfo": null
  }

Here, ``sourceCount`` is the number of source lines of code (SLOC),
``documentationCount`` the number of lines containing comments and
``emptyCount`` the number of empty lines (which includes "no operation"
lines).

The ``state`` can have one of the following values:

* analyzed: successfully analyzed
* binary: the file is a  :ref:`binary file <binary>`
* duplicate: the file is a :ref:`duplicate <duplicates>` of another
* empty: the file is empty (file size = 0)
* error: the source could not be parsed; in this case, ``stateInfo``
  contains a message with more details
* generated: the file has been generated as specified with :option:`--generated`
* unknown: pygments does not offer any lexer to analyze the file

In ``languages`` the summary for each language is available, for example:

.. code-block:: JavaScript

  {
    "documentationCount": 406,
    "emptyCount": 631,
    "fileCount": 18,
    "isPseudoLanguage": false,
    "language": "Python",
    "sourceCount": 2332
  }

In ``summary`` the total counts across the whole project can be accessed, for
example:

.. code-block:: JavaScript

  "summary": {
    "totalDocumentationCount": 410,
    "totalEmptyCount": 869,
    "totalFileCount": 32,
    "totalSourceCount": 2930
  }

The ``runtime`` entry collects general information about how well pygount performed
in collecting the information, for example:

.. code-block:: JavaScript

  "runtime": {
    "durationInSeconds": 0.712625,
    "filesPerSecond": 44.904402736362044
    "finishedAt": "2022-01-05T11:49:27.009310",
    "linesPerSecond": 5906.332222417121,
    "startedAt": "2022-01-05T11:49:26.296685",
  }


Pretty printing
---------------

Because the output is concise and consequently mostly illegible for a
human reader, you might want to pipe it through a pretty printer. As you
already have python installed, the easiest way is:

.. code-block:: sh

  pygount --format json | python -m json.tool

Another alternativ would be `jq <https://stedolan.github.io/jq/>`_:

.. code-block:: sh

  pygount --format json | jq .
