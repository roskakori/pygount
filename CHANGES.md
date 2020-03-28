# Pygount version history

Version 1.2.0, 2020-03-TODO

* Changed installation to fail when attempting to install on Python earlier
  than 3.5.
* Improved API:
  * `SourceAnalysis.state` is now a proper enum instead of a string.
* Cleaned up project:
  * Changed continuous integration from Travis CI to Github actions in the hope
    that the CI build does not automatically break after a while because
    things constantly change in the CI backend.
  * Changed README format from reStructuredText to Markdown.
  * Improved badges in README: added a badge for supported Python versions
    and unified the layout by using <https://shields.io>.
  * Removed obsolete development files (for ant, tox etc).

Version 1.1.0, 2020-03-10

* Fixed `--folders_to_skip` and `--names-to-skip` which simply were ignored
  (contributed by pclausen, issue
  [#17](https://github.com/roskakori/pygount/issues/17)).
* Added option `--format=summary` to get a language overview and sum total
  (based on a contribution by Yuriy Petrovskiy, issue
  [#16](https://github.com/roskakori/pygount/issues/16)).
* Added Python 3.7 and 3.8 to the list of supported versions.
* Dropped support for Python 3.3 and 3.4, mostly because it became hard to
  test without going through major hoops.

Version 1.0.0, 2017-07-04

* Fixed confusing warning about XML file `<unknown>` caused by SAX parser.
  As a workaround, `<unknown>` is now replaced by the actual path of the
  XML file that cannot be parsed.
* Added Python 3.6 to the list of supported versions  (issue
  [#14](https://github.com/roskakori/pygount/issues/14)).

Version 0.9, 2017-05-04

* Fixed `AssertionError` when option `--encoding=chardet` was specified.
* Changed warning message "no fallback encoding specified, using](encoding>"
  to a debug message because it did not add any interesting information as
  the encoding actually used is visible in the info message for each file.
* Added detection of binary files and excluded them from the analysis. In
  particular Django model objects (`*.mo`) are not considered Modelica
  source code anymore (issue
  [#11](https://github.com/roskakori/pygount/issues/11)).
* Added detection of DocBook XML by DTD (issue
  [#10](https://github.com/roskakori/pygount/issues/10)).
* Added support for suffices to indicate PL/SQL files according to
  `Oracle FAQ entry on file extensions](http://www.orafaq.com/wiki/File_extensions)
  (issue [#12](https://github.com/roskakori/pygount/issues/12)).
* Added possibility to specify a fallback encoding for encoding 'chardet'. Use
  e.g. `--encoding=chardet;cp1252`.

Version 0.8, 2016-10-07

* Fixed option `--verbose`. Now each analyzed source code results in at least
  one informational message in the log.
* Added detection of duplicates using size and then MD5 code as criteria (issue
  [#2](https://github.com/roskakori/pygount/issues/2)). Use the option
  `--duplicates` to still count duplicate source code.
* Improved detetion of programming language, which is now more consistent and
  yields the same language between Python invocations.

Version 0.7, 2016-09-28

* Fixed that option `--generated` was ignored.
* Added support for a couple of languages not supported by `pygments` yet:

  * m4, VBScript and WebFOCUS use minimalistic lexers that can distinguish
    between comments and code.
  * OMG IDL repurposes the existing Java lexer.

* Added detection of certain XML dialects as separate language (issue
  [#8](https://github.com/roskakori/pygount/issues/8)).

Version 0.6, 2016-09-26

* Fixed that source files could end up as `__error__` if the first non ASCII
  characters showed up only after 16 kilobyte and the encoding was not UTF-8.
  Now pygount attempts to read the whole file as UTF-8 before assuming it
  actually is UTF-8.
* Changed lines in plain text files to count as comments (issue
  [#9](https://github.com/roskakori/pygount/issues/9)). Before pygments
  treated them as `ResourceBundle`.
* Changed that empty files have `__empty__` as language (issue
  [#7](https://github.com/roskakori/pygount/issues/7)).
* Extended workaround for
  [pygments issue #1284](https://bitbucket.org/birkenfeld/pygments-main/issues/1284)
  to replace any lexer `*+Evoque` by `*`.

Version 0.5, 2016-09-22

* Added that generated source code is excluded from analysis (issue
  [#1](https://github.com/roskakori/pygount/issues/1)). Use option
  `--generated` to specify patterns that indicate generated code.
* Added workaround for pygments sometimes detecting the same XML file as XML
  and other times as XML+Evoque (probably depending on the hash seed). Now
  XML+Evoque  is always changed to XML.
* Added `__pycache__` as default `--folder-to-skip`.
* Added notes on pseudo languages for source code that cannot be analyzed.

Version 0.4, 2016-09-11

* Fixed `LookupError` on broken encoding in magic comment (issue
  [#4](https://github.com/roskakori/pygount/issues/4)).
* Added options `--folders-to-skip` and `--names-to-skip` to specify which
  files should be excluded from analysis.
* Added comma (`,`) and colon (`:`) to list of "white characters" that do
  not count as code if there is nothing else in the line.
* Improved pattern matching: for all options that according to `--help`
  take `PATTERNS` you can now specify that the patterns are regular
  expressions instead of shell patterns (using `[regex]`) and that they
  should extend the default patterns (using `[...]`).
* Improved documentation: added notes on how code is counted and how pygount
  compares to other similar tools.

Version 0.3, 2016-08-20

* Fixed `@rem` comments in DOS batch files (issue
  [#3](https://github.com/roskakori/pygount/issues/3)).
* Cleaned up code.

Version 0.2, 2016-07-10

* Fixed that files starting with underscore (e.g. `__init__.py`) were
  excluded from analysis.
* Changed `chardet` package to be optional.
* Added possibility to specify single files and glob patterns to analyze.
* Added that lines containing only certain characters are treated as white
  space instead of code. Currently this concerns brackets (`()[]{}`) and
  semicolon (`;`).
* Added that Python's `pass` statement is treated as white space instead of
  code.
* Cleaned up and (slightly) optimized code.

Version 0.1, 2016-07-05

* Initial public release.
