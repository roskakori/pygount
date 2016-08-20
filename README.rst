.. image:: https://travis-ci.org/roskakori/pygount.svg?branch=master
    :target: https://travis-ci.org/roskakori/pygount
    :alt: Build Status

.. image:: https://coveralls.io/repos/roskakori/pygount/badge.png?branch=master
    :target: https://coveralls.io/r/roskakori/pygount?branch=master
    :alt: Test coverage

.. image:: https://landscape.io/github/roskakori/pygount/master/landscape.svg?style=flat
    :target: https://landscape.io/github/roskakori/pygount/master
    :alt: Code Health


pygount
=======

Pygount is a command line tool to scan folders for source code files and
count the number of source code lines in it. It is similar to tools like
`sloccount <http://www.dwheeler.com/sloccount/>`_ and
`cloc <http://cloc.sourceforge.net/>`_ but uses the
`pygments <http://pygments.org/>`_
package to analyze the source code and consequently can analyze any
`programming language supported by pygments <http://pygments.org/languages/>`_.

The name is a combination of pygments and count.


Download and installation
-------------------------

Pygount is available from https://pypi.python.org/pypi/pygount and can be
installed running::

  $ pip install pygount


Usage
-----

Simply run and specify the folder to analyze recursively, for example::

  $ pygount ~/development/sometool

If you omit the folder, the current folder of your shell is used as starting
point. Apart from folders you can also specify single files and glob patterns
(using ``?``, ``*`` and ranges like ``[a-z]``).

Certain files and folders are automatically excluded from the analysis:

* files starting with dot (.) or ending in tilda (~)
* folders starting with dot (.) or underscore (_) or ending in tilda (~)

To limit the analysis on certain files, you can specify a comma separated list
of suffices to take into account, for example ``--suffix=py,sql,xml``.

By default the result of the analysis are written to the standard output in a
format similar to sloccount. To redirect the output to a file, use e.g.
``--out=counts.txt``. To change the format to an XML file similar to cloc, use
``--format=cloc-xml``.

When reading source code, pygount automatically detects the encoding. It uses
a simple algorithm where it recognizes BOM, XML declaractions such as::

  <?xml encoding='cp1252'?>

and "magic" comments such as::

  # -*- coding: cp1252 -*-

If the file does not have an appropriate heading, pygount attempts to read it
using UTF-8. If this fails, it reads the file using a fallback encoding (by
default CP1252) and ignores any encoding errors.

You can change this behavior using the ``--encoding`` option:

* To keep the automatic analysis and use a different fallback encoding specify
  for example ``--encoding=automatic;iso-8859-15``
* To use an automatic detection based on heuristic, use
  ``--encoding=chardet``. For this to work, the
  `chardet <https://pypi.python.org/pypi/chardet>`_ package must be installed,
* To use a specific encoding (for all files analyzed), use for example
  ``--encoding=iso-8859-15``.

To get a description of all the available command line options, run::

  $ pygount --help


API
---

Pygount provides a simple API to integrate it in other tools. This however is
currently still a work in progress and subject to change.

Here's an example on how to analyze one of pygount's own source codes::

  >>> import pygount
  >>> analysis = pygount.source_analysis('pygount/analysis.py', 'pygount')
  >>> analysis
  SourceAnalysis(path='pygount/analysis.py', language='Python', group='pygount', code=164, documentation=48, empty=27, string=0)


Continuous integration
----------------------

Pygount can produce output that can be processed by the
`SLOCCount plug-in <https://wiki.jenkins-ci.org/display/JENKINS/SLOCCount+Plugin>`_
for the `Jenkins <https://jenkins.io/>`_ continuous integration server.

For example::

  pygount --format=cloc-xml --out cloc.xml --suffix=py --verbose

Then add a post-build action "Publish SLOCCount analysis results" and set
"SLOCCount report" to "cloc.xml".


Version history
---------------

Version 0.3, 2016-08-20

* Fixed ``@rem`` comments in DOS batch files (issue
  `#3 <https://github.com/roskakori/pygount/issues/3>`_).
* Cleaned up code.

Version 0.2, 2016-07-10

* Fixed that files starting with underscore (e.g. ``__init__.py``) were
  excluded from analysis.
* Changed ``chardet`` package to be optional.
* Added possibility to specify single files and glob patterns to analyze.
* Added that lines containing only certain characters are treated as white
  space instead of code. Currently this concerns brackets (``()[]{}``) and
  semicolon (``;``).
* Added that Python's ``pass`` statement is treated as white space instead of
  code.
* Cleaned up and (slightly) optimized code.

Version 0.1, 2016-07-05

* Initial public release.
