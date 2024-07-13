Changes
#######

This chapter describes the changes coming with each new version of pygount.

Version 1.8.1, 2024-07-xx

* Development: Change linter to ruff and in turn clean up code (issue
  `#157 <https://github.com/roskakori/pygount/issues/157>`_).
* Development: Change default branch to main (issue
  `#160 <https://github.com/roskakori/pygount/issues/160>`_).
* Removed deprecated code: (contributed by Marco Gambone and Niels Vanden Bussche, issue
  `#47 <https://github.com/roskakori/pygount/issues/47>`_).

Version 1.8.0, 2024-05-13

* Add all available counts and percentages to JSON format (issue
  `#122 <https://github.com/roskakori/pygount/issues/122>`_).

  In particular, this makes available the ``codeCount``, which is similar to
  the already existing ``sourceCount`` but does exclude lines that contain
  only strings. You can check their availability by validating that the
  ``formatVersion`` is at least 1.1.0.

  The documentation about ":ref:`How to count code`" has more information
  about the available counts and the ways they are computed.

  Pygount 2.0 will probably introduce some breaking changes in this area,
  which can already be previewed and discussed at issue
  `#152 <https://github.com/roskakori/pygount/issues/152>`_.

Version 1.7.0, 2024-05-13

* Fix analysis with
  `FIPS <https://en.wikipedia.org/wiki/Federal_Information_Processing_Standards>`_
  mode by changing computation of hash for duplicate detection from MD5 to
  SHA256. As side effect, reasonably modern machines should receive a
  (probably unnoticeable) minor performance boost (contributed by Matthew
  Vine, issue `#137 <https://github.com/roskakori/pygount/issues/137>`_).
* Add command line option ``--merge-embedded-languages`` to merge embedded
  languages into their base language. For example, "HTML+Django/Jinja" counts
  as "HTML" (issue `#105 <https://github.com/roskakori/pygount/issues/105>`_).
* Add Python 3.12 and made it the main version for CI (issue
  `#145 <https://github.com/roskakori/pygount/issues/145>`_).

Version 1.6.1, 2023-07-02

* Fixed missing check for seekable file handles (issue
  `#114 <https://github.com/roskakori/pygount/issues/114>`_).
* Fixed the ReadTheDocs documentation build by switching to the built-in
  alabaster Sphinx theme (issue
  `#116 <https://github.com/roskakori/pygount/issues/116>`_).

Version 1.6.0, 2023-06-26

* Add support for analysis of remote git URL's in addition to local files
  (contributed by Rojdi Thomallari, issue
  `#109 <https://github.com/roskakori/pygount/issues/109>`_).
* Removed support for Python 3.7.
* Improved API:

  * Add option to pass a file handle to ``SourceAnalysis.from_file()``
    (contributed by Dominik George, issue
    `#100 <https://github.com/roskakori/pygount/issues/100>`_).

Version 1.5.1, 2023-01-02

* Removed progress bar for ``--format=sloccount`` because it resulted into
  blank lines when running on Windows and could cause interwoven output on
  Unix (issue `#91 <https://github.com/roskakori/pygount/issues/91>`_).

Version 1.5.0, 2022-12-30

* Removed support for Python 3.6 and updated dependencies (issue
  `#93 <https://github.com/roskakori/pygount/issues/93>`_).

Version 1.4.0, 2022-04-09

* Added progress bar during scan phase and improved visual design of
  ``--format=summary`` (contributed by Stanislav Zmiev, issue
  `#73 <https://github.com/roskakori/pygount/issues/73>`_).
* Added percentages to API. For example in addition to
  ``code_count`` now there also is ``code_percentage``.

Version 1.3.0, 2022-01-06

* Fixed computation of "lines per second", which was a copy and paste of
  "files per second".

* Added JSON as additional output :option:`--format`, see :doc:`json` for
  details (issue `#62 <https://github.com/roskakori/pygount/issues/62>`_).

* Added detection of
  `GitHub community files <https://docs.github.com/en/communities/setting-up-your-project-for-healthy-contributions>`_
  without suffix as text (issue
  `#54 <https://github.com/roskakori/pygount/issues/54>`_).

* Changed build process to `poetry <https://python-poetry.org/>`_ to change
  several messy configuration files into a single even more messy
  configuration file.

Version 1.2.5, 2021-05-16

* Removed support for Python 3.5. Probably it still works but there is no easy
  way to test this anymore because 3.5 has reached end of life a while ago.


Version 1.2.4, 2020-08-11

* Fixed scanning of "." (for current folder), which was skipped entirely
  (issue `#56 <https://github.com/roskakori/pygount/issues/56>`_).


Version 1.2.3, 2020-07-05

* Improved detection of text files by trying to guess a lexer for
  :file:`*.txt` before assuming it is text. This basically fixes the detection
  of :file:`CMakelists.txt` as CMake file
  `#53 <https://github.com/roskakori/pygount/issues/53>`_). However, it will
  only work with some files due to multiple issues with the regular expression
  Pygments uses in versions up to 2.6.1 to detect CMake headers. This should
  be fixed once pull request
  `#1491 <https://github.com/pygments/pygments/pull/1491>`_ is applied.

Version 1.2.2, 2020-06-24

* Changed preprocessor statements to count as code, unlike Pygments which
  treats them as special comments (contributed by nkr0, issue
  `#51 <https://github.com/roskakori/pygount/issues/51>`_).

Version 1.2.1, 2020-04-02

* Fixed broken links in README on PyPI by moving the documentation to
  `ReadTheDocs <https://pygount.readthedocs.io/>`_.
* Improved API:

  * Changed factory functions to methods and added deprecation warnings:

    * :py:func:`source_analysis` → :py:meth:`SourceAnalysis.from_file`
    * :py:func:`pseudo_source_analysis` → :py:meth:`SourceAnalysis.from_state`

  * Changed attributes in :py:class:`SourceAnalysis` to read-only properties.
  * Renamed properties holding counts from :py:attr:`xxx` to
    :py:attr:`xxx_count`.
  * Added API reference to documentation.
  * Added a couple of type hints and assertions.

Version 1.2.0, 2020-03-30

* Added file count to summary.
* Changed installation to fail when attempting to install on Python earlier
  than 3.5.
* Improved API:

  * Changed :py:attr:`SourceAnalysis.state` to be a proper enum instead of a string.
  * Added :py:class:`ProjectSummary` to summarize multiple files.

* Cleaned up project:

  * Changed continuous integration from Travis CI to Github actions in the hope
    that the CI build does not automatically break after a while because
    things constantly change in the CI backend.
  * Changed README format from reStructuredText to Markdown.
  * Improved badges in README: added a badge for supported Python versions
    and unified the layout by using <https://shields.io>.
  * Removed obsolete development files (for ant, tox etc).

Version 1.1.0, 2020-03-10

* Fixed :option:`--folders-to-skip` and :option:`--names-to-skip` which simply
  were ignored (contributed by pclausen, issue
  `#17 <https://github.com/roskakori/pygount/issues/17>`_).
* Added option ``--format=summary`` to get a language overview and sum total
  (based on a contribution by Yuriy Petrovskiy, issue
  `#16 <https://github.com/roskakori/pygount/issues/16>`_).
* Added Python 3.7 and 3.8 to the list of supported versions.
* Dropped support for Python 3.3 and 3.4, mostly because it became hard to
  test without going through major hoops.

Version 1.0.0, 2017-07-04

* Fixed confusing warning about XML file ``<unknown>`` caused by SAX parser.
  As a workaround, ``<unknown>`` is now replaced by the actual path of the
  XML file that cannot be parsed.
* Added Python 3.6 to the list of supported versions  (issue
  `#14 <https://github.com/roskakori/pygount/issues/14>`_).

Version 0.9, 2017-05-04

* Fixed :py:exc:`AssertionError` when option
  :option:`--encoding=chardet <--encoding>` was specified.
* Changed warning message "no fallback encoding specified, using](encoding>"
  to a debug message because it did not add any interesting information as
  the encoding actually used is visible in the info message for each file.
* Added detection of binary files and excluded them from the analysis. In
  particular Django model objects (``*.mo``) are not considered Modelica
  source code anymore (issue
  `#11 <https://github.com/roskakori/pygount/issues/11>`_).
* Added detection of DocBook XML by DTD (issue
  `#10 <https://github.com/roskakori/pygount/issues/10>`_).
* Added support for suffices to indicate PL/SQL files according to
  `Oracle FAQ entry on file extensions <http://www.orafaq.com/wiki/File_extensions>`_
  (issue `#12 <https://github.com/roskakori/pygount/issues/12>`_).
* Added possibility to specify a fallback encoding for encoding 'chardet'. Use
  e.g. :option:`--encoding=chardet;cp1252 <--encoding>`.

Version 0.8, 2016-10-07

* Fixed option :option:`--verbose`. Now each analyzed source code results in
  at least one informational message in the log.
* Added detection of duplicates using size and then MD5 code as criteria (issue
  `#2 <https://github.com/roskakori/pygount/issues/2>`_). Use the option
  :option:`--duplicates` to still count duplicate source code.
* Improved detetion of programming language, which is now more consistent and
  yields the same language between Python invocations.

Version 0.7, 2016-09-28

* Fixed that option :option:`--generated` was ignored.
* Added support for a couple of languages not supported by :py:mod:`pygments` yet:

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
  treated them as :py:class:`ResourceBundle`.
* Changed that empty files have ``__empty__`` as language (issue
  `#7 <https://github.com/roskakori/pygount/issues/7>`_).
* Extended workaround for
  `pygments issue #1284  <https://bitbucket.org/birkenfeld/pygments-main/issues/1284>`_
  to replace any lexer ``*+Evoque`` by ``*``.

Version 0.5, 2016-09-22

* Added that generated source code is excluded from analysis (issue
  `#1 <https://github.com/roskakori/pygount/issues/1>`_). Use option
  :option:`--generated` to specify patterns that indicate generated code.
* Added workaround for pygments sometimes detecting the same XML file as XML
  and other times as XML+Evoque (probably depending on the hash seed). Now
  XML+Evoque  is always changed to XML.
* Added :file:`__pycache__` as default :option:`--folders-to-skip`.
* Added notes on pseudo languages for source code that cannot be analyzed.

Version 0.4, 2016-09-11

* Fixed :py:exc:`LookupError` on broken encoding in magic comment (issue
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

* Fixed that files starting with underscore (e.g. :file:`__init__.py`) were
  excluded from analysis.
* Changed :py:mod:`chardet` package to be optional.
* Added possibility to specify single files and glob patterns to analyze.
* Added that lines containing only certain characters are treated as white
  space instead of code. Currently this concerns brackets (``()[]{}``) and
  semicolon (``;``).
* Added that Python's ``pass`` statement is treated as white space instead of
  code.
* Cleaned up and (slightly) optimized code.

Version 0.1, 2016-07-05

* Initial public release.
