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

Pygount is open source and distributed under the
`BSD license <https://opensource.org/licenses/BSD-3-Clause>`_. The source
code is available from https://github.com/roskakori/pygount.


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
point. Apart from folders you can also specify single files and shell patterns
(using ``?``, ``*`` and ranges like ``[a-z]``).

Certain files and folders are automatically excluded from the analysis:

* files starting with dot (.) or ending in tilda (~)
* folders starting with dot (.) or named ``_svn``.

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


Patterns
--------

Some command line arguments take patterns as values.

By default, patterns are shell patterns using ``*``, ``?`` and ranges like
``[a-z]`` as placeholders. Depending on your platform, the are case sensitive
(Unix) or not (Mac OS, Windows).

If a pattern starts with ``[regex]`` you can specifiy a comma separated list
of regular expressions instead using all the constructs supported by the
`Python regular expression syntax <https://docs.python.org/3/library/re.html#regular-expression-syntax>`_.
Regular expressions are case sensitive unless they include a ``(?i)`` flag.

If the first actual pattern is ``[...]`` default patterns are included.
Without it, defaults are ignored and only the pattern explicitely stated are
taken into account.

So for example to specify that generated code can also contain the German word
"Generiert" in a case insensivie way use
``--generated=[regex][...](?i).*generiert``.


Source code encoding
--------------------

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


Pseudo languages
----------------

If a source code is not counted, the number of lines is 0 and the language
shown is a pseudo language indicating the reason:

* __duplicate__ - the source code is a bytewise identical copy of another
  file; enable the command line option ``--duplicates`` to also count code in
  duplicates (and gain a minor performance improvement)
* __empty__ - the source code is an empty file with a size of 0 bytes.
* __error__ - the source code could not be parsed e.g. due an I/O error.
* __generated__ - the source code is generated according to the command line
  option ``--generated``.
* __unknown__ - pygments does not provide a lexer to parse the source code.


Other information
-----------------

To get a description of all the available command line options, run::

  $ pygount --help

To get the version number, run::

  $ pygount --version


Continuous integration
----------------------

Pygount can produce output that can be processed by the
`SLOCCount plug-in <https://wiki.jenkins-ci.org/display/JENKINS/SLOCCount+Plugin>`_
for the `Jenkins <https://jenkins.io/>`_ continuous integration server.

For example::

  pygount --format=cloc-xml --out cloc.xml --suffix=py --verbose

Then add a post-build action "Publish SLOCCount analysis results" and set
"SLOCCount report" to "cloc.xml".


How pygount counts code
-----------------------

Pygount basically counts physical lines of source code.

First, it lexes the code using the lexers ``pygments`` assigned to it. If
``pygments`` cannot find an appropriate lexer, pygount has a few additional
internal lexers that can at least distinguish between code and comments:

* m4, VBScript and WebFOCUS use minimalistic lexers that can distinguish
  between comments and code.
* OMG IDL repurposes the existing Java lexer.

Furthermore plain text has a separate lexer that counts all lines as comments.

Lines that only contain comment tokens and white space count as comments.
Lines that only contain white space are not taken into account. Everything
else counts as code.

If a line contains only "white characters" it is not taken into account
presumably because the code is only formatted that way to make it easier to
read. Currently white characters are::

    (),:;[]{}

Because of that, pygount reports about 10 to 20 percent fewer SLOC for C-like
languages than other similar tools.

For some languages "no operations" are detected and treated as white space.
For example Python's ``pass`` or Transact-SQL's ``begin`` and ``end`` .

As example consider this Python code::

    class SomeError(Exception):
        """
        Some error caused by some issue.
        """
        pass

This counts as 1 line of code and 3 lines of comments. The line with ``pass``
is considered a "no operation" and thus not taken into account.


Comparison with other tools
---------------------------

Pygount can analyze more languages than other common tools such as sloccount
or cloc because it builds on ``pygments``, which provides lexers for hundreds
of languages. This also makes it easy to support another language: simply
`write your own lexer <http://pygments.org/docs/lexerdevelopment/>`_.

For certain corner cases pygount give more accurate results because it
actually lexes the code unlike other tools that mostly look for comment
markers and can get confused when they show up inside strings. In practice
though this should not make much of a difference.

Pygount is slower than most other tools. Partially this is due to actually
lexing instead of just scanning the code. Partially other tools can use
statically compiled languages such as Java or C, which are generally faster
than dynamic languages. For many applications though pygount should be
"fast enough", especially when called during a nightly build.


API
---

Pygount provides a simple API to integrate it in other tools. This however is
currently still a work in progress and subject to change.

Here's an example on how to analyze one of pygount's own source codes::

  >>> import pygount
  >>> analysis = pygount.source_analysis('pygount/analysis.py', 'pygount')
  >>> analysis
  SourceAnalysis(path='pygount/analysis.py', language='Python', group='pygount', code=302, documentation=66, empty=62, string=23, state='analyzed', state_info=None)


Version history
---------------

Version 0.8, 2016-10-xx

* Fixed option ``--verbose``. Now each analyzed source code results in at least
  one informational message in the log.
* Added detection of duplicates using size and then MD5 code as criteria (issue
  `#2 <https://github.com/roskakori/pygount/issues/2>`_). Use the option
  ``--duplicates`` to still count duplicate source code.
* Improved detetion of programming language, which now is more consistent
  and yields the same language between Python invocations.

Version 0.7, 2016-09-28

* Fixed that option ``--generated`` was ignored.
* Added support for a couple of languages not supported by ``pygments`` yet:

  * m4, VBScript and WebFOCUS use minimalistic lexers that can distinguish
    between comments and code.
  * OMG IDL repurposes the existing Java lexer.

* Added detection of certain XML dialects as separate language (issue
  `#8 <https://github.com/roskakori/pygount/issues/8>`_).

Version 0.6, 2016-09-26

* Fixed that source files could end up as ``__error__`` if the first non ASCII
  characters showed up only after 16 kilobyte and the encoding was not UTF-8.
  Now pygount attempts to read the whole file as UTF-8 before assuming it
  actually is UTF-8.
* Changed lines in plain text files to count as comments (issue
  `#9 <https://github.com/roskakori/pygount/issues/9>`_). Before pygments
  treated them as `ResourceBundle`.
* Changed that empty files have ``__empty__`` as language (issue
  `#7 <https://github.com/roskakori/pygount/issues/7>`_).
* Extended workaround for
  `pygments issue #1284 <https://bitbucket.org/birkenfeld/pygments-main/issues/1284>`_
  to replace any lexer ``*+Evoque`` by ``*``.

Version 0.5, 2016-09-22

* Added that generated source code is excluded from analysis (issue
  `#1 <https://github.com/roskakori/pygount/issues/1>`_). Use option
  ``--generated`` to specify patterns that indicate generated code.
* Added workaround for pygments sometimes detecting the same XML file as XML
  and other times as XML+Evoque (probably depending on the hash seed). Now
  XML+Evoque  is always changed to XML.
* Added ``__pycache__`` as default ``--folder-to-skip``.
* Added notes on pseudo languages for source code that cannot be analyzed.

Version 0.4, 2016-09-11

* Fixed ``LookupError`` on broken encoding in magic comment (issue
  `#4 <https://github.com/roskakori/pygount/issues/4>`_).
* Added options ``--folders-to-skip`` and ``--names-to-skip`` to specify which
  files should be excluded from analysis.
* Added comma (``,``) and colon (``:``) to list of "white characters" that do
  not count as code if there is nothing else in the line.
* Improved pattern matching: for all options that according to ``--help``
  take ``PATTERNS`` you can now specify that the patterns are regular
  expressions instead of shell patterns (using ``[regex]``) and that they
  should extend the default patterns (using ``[...]``).
* Improved documentation: added notes on how code is counted and how pygount
  compares to other similar tools.

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
