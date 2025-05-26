# Changes

This chapter describes the changes coming with each new version of
pygount.

## Version 3.1.0, 2025-05-27

- Add command line option [`--generated-names`](usage.md#-generated-names) to specify which file names should be considered to be generated. The current patterns recognized are somewhat limited, so contributions are welcome. See the section on "[Generated files](background.md#generated-files)" for hints on how to do that (issue [#190](https://github.com/roskakori/pygount/issues/190)).
- Change documentation from Sphinx to MkDocs in the hope to avoid it breaking regularly (issue [#191](https://github.com/roskakori/pygount/issues/191)).

Development:

- Replace `format()` with f-strings (contributed by Ben Allen, issue [#166](https://github.com/roskakori/pygount/issues/166)).
- Change sdist archive to include more than just the Python source code.

## Version 3.0.0, 2025-05-23

- Count pure markup files as documentation: (contributed by Tytus Bucholc, issue [#6](https://github.com/roskakori/pygount/issues/6)).
- Fix silent error on git failing (contributed by Tom De Bièvre, issue [#162](https://github.com/roskakori/pygount/issues/162))
- Transform common project URLs to repository: (contributed by Tom De Bièvre, issue [#164](https://github.com/roskakori/pygount/issues/164))
- Change dependency rules for rich to be more lenient (suggested by Brian McGillion, issue [#193](https://github.com/roskakori/pygount/issues/193))

## Version 2.0.0, 2025-03-16

- Fix `TypeError` when processing files with a magic encoding comment specifying an unknown encoding and using `--format=json` (contributed by PyHedgehog, issue [#176](https://github.com/roskakori/pygount/issues/176))
- Fix false positives when extracting the encoding from magic coding comments (issue [#184](https://github.com/roskakori/pygount/issues/184))
- Add support for Python 3.13 and later (issue [#174](https://github.com/roskakori/pygount/issues/174))
- Remove temporary directory in the output of a git analysis (contributed by Isabel Beckenbach, issue [#113](https://github.com/roskakori/pygount/issues/113))
- Remove support for Python 3.8 (issue [#158](https://github.com/roskakori/pygount/issues/158))
- Development: Change packaging to uv (issue [#180](https://github.com/roskakori/pygount/issues/180)).
- Development: Change linter to ruff and in turn, clean up code (issue [#157](https://github.com/roskakori/pygount/issues/157)).
- Development: Change default branch to main (issue [#160](https://github.com/roskakori/pygount/issues/160)).
- Removed deprecated code: (contributed by Marco Gambone and Niels Vanden Bussche, issue [#47](https://github.com/roskakori/pygount/issues/47)).

## Version 1.8.0, 2024-05-13

- Add all available counts and percentages to JSON format (issue [#122](https://github.com/roskakori/pygount/issues/122)).

  In particular, this makes available the `codeCount`, which is similar to the already existing `sourceCount` but does exclude lines that contain only strings. You can check their availability by validating that the `formatVersion` is at least 1.1.0.

  The documentation about "`How to count code` has more information about the available counts and the ways they are computed.

  Pygount 2.0 will probably introduce some breaking changes in this area, which can already be previewed and discussed at issue [#152](https://github.com/roskakori/pygount/issues/152).

## Version 1.7.0, 2024-05-13

- Fix analysis with [FIPS](https://en.wikipedia.org/wiki/Federal_Information_Processing_Standards) mode by changing computation of hash for duplicate detection from MD5 to SHA256. As a side effect, reasonably modern machines should receive a (probably unnoticeable) minor performance boost (contributed by Matthew Vine, issue [#137](https://github.com/roskakori/pygount/issues/137)).
- Add command line option `--merge-embedded-languages` to merge embedded languages into their base language. For example, "HTML+Django/Jinja" counts as "HTML" (issue [#105](https://github.com/roskakori/pygount/issues/105)).
- Add Python 3.12 and make it the main version for CI (issue [#145](https://github.com/roskakori/pygount/issues/145)).

## Version 1.6.1, 2023-07-02

- Fix missing check for seekable file handles (issue [#114](https://github.com/roskakori/pygount/issues/114)).
- Fix the ReadTheDocs documentation build by switching to the built-in alabaster Sphinx theme (issue [#116](https://github.com/roskakori/pygount/issues/116)).

## Version 1.6.0, 2023-06-26

- Add support for analysis of remote git URL\'s in addition to local files (contributed by Rojdi Thomallari, issue [#109](https://github.com/roskakori/pygount/issues/109)).
- Removed support for Python 3.7.
- Improve API:
  - Add an option to pass a file handle to `SourceAnalysis.from_file()` (contributed by Dominik George, issue [#100](https://github.com/roskakori/pygount/issues/100)).

## Version 1.5.1, 2023-01-02

- Remove progress bar for `--format=sloccount` because it resulted into blank lines when running on Windows and could cause interwoven output on Unix (issue [#91](https://github.com/roskakori/pygount/issues/91)).

## Version 1.5.0, 2022-12-30

- Remove support for Python 3.6 and update dependencies (issue [#93](https://github.com/roskakori/pygount/issues/93)).

## Version 1.4.0, 2022-04-09

- Add progress bar during scan phase and improve visual design of `--format=summary` (contributed by Stanislav Zmiev, issue [#73](https://github.com/roskakori/pygount/issues/73)).
- Add percentages to API. For example in addition to `code_count` now there also is `code_percentage`.

## Version 1.3.0, 2022-01-06

- Fix computation of "lines per second", which was a copy and paste of "files per second".
- Add JSON as additional output `--format`, see [JSON](json.md) for details (issue [#62](https://github.com/roskakori/pygount/issues/62)).
- Add detection of [GitHub community files](https://docs.github.com/en/communities/setting-up-your-project-for-healthy-contributions) without a suffix as text (issue [#54](https://github.com/roskakori/pygount/issues/54)).
- Change the build process to [poetry](https://python-poetry.org/) to change several messy configuration files into a single even more messy configuration file.

## Version 1.2.5, 2021-05-16

- Remove support for Python 3.5. Probably it still works, but there is no easy way to test this anymore because 3.5 reached its end of life a while ago.

## Version 1.2.4, 2020-08-11

- Fix scanning of "." (for current folder), which was skipped entirely (issue [#56](https://github.com/roskakori/pygount/issues/56)).

## Version 1.2.3, 2020-07-05

- Improve detection of text files by trying to guess a lexer for `*.txt` before assuming it is text. This basically fixes the detection of `CMakelists.txt` as CMake file [#53](https://github.com/roskakori/pygount/issues/53)). However, it will only work with some files due to multiple issues with the regular expression Pygments used in versions up to 2.6.1 to detect CMake headers. This should be fixed once pull request
  [#1491](https://github.com/pygments/pygments/pull/1491) is applied.

## Version 1.2.2, 2020-06-24

- Changed preprocessor statements to count as code, unlike Pygments which treats them as special comments (contributed by nkr0, issue [#51](https://github.com/roskakori/pygount/issues/51)).

## Version 1.2.1, 2020-04-02

- Fix broken links in README on PyPI by moving the documentation to [ReadTheDocs](https://pygount.readthedocs.io/).
- Improv API:
  - Change factory functions to methods and added deprecation warnings:
    - `source_analysis` → `SourceAnalysis.from_file`
    - `pseudo_source_analysis` → `SourceAnalysis.from_state`
  - Change attributes in `SourceAnalysis` to read-only properties.
  - Rename properties holding counts from `xxx` to `xxx_count`.
  - Add API reference to documentation.
  - Add a couple of type hints and assertions.

## Version 1.2.0, 2020-03-30

- Add file count to summary.
- Change installation to fail when attempting to install on Python earlier than 3.5.
- Improve API:
  - Change `SourceAnalysis.state` to be a proper enum instead of a string.
  - Add `ProjectSummary` to summarize multiple files.
- Clean up the project:
  - Change continuous integration from Travis CI to GitHub actions in the hope that the CI build does not automatically break after a while because things constantly change in the CI backend.
  - Change README format from reStructuredText to Markdown.
  - Improve badges in README: added a badge for supported Python versions and unified the layout by using <https://shields.io>.
  - Remove obsolete development files (for ant, tox etc).

## Version 1.1.0, 2020-03-10

- Fix `--folders-to-skip` and `--names-to-skip` which simply were
  ignored (contributed by pclausen, issue [#17](https://github.com/roskakori/pygount/issues/17)).
- Add option `--format=summary` to get a language overview and sum total (based on a contribution by Yuriy Petrovskiy, issue [#16](https://github.com/roskakori/pygount/issues/16)).
- Add Python 3.7 and 3.8 to the list of supported versions.
- Drop support for Python 3.3 and 3.4, mostly because it became hard to test without going through major hoops.

## Version 1.0.0, 2017-07-04

- Fix confusing warning about XML file `<unknown>` caused by SAX parser. As a workaround, `<unknown>` is now replaced by the actual path of the XML file that cannot be parsed.
- Add Python 3.6 to the list of supported versions (issue [#14](https://github.com/roskakori/pygount/issues/14)).

## Version 0.9, 2017-05-04

- Fix `AssertionError` when option `--encoding=chardet` was specified.
- Change the warning message "no fallback encoding specified, using \<encoding\>" to a debug message because it did not add any interesting information as the encoding actually used is visible in the info message for each file.
- Add detection of binary files and exclude them from the analysis. In particular Django model objects (`*.mo`) are not considered Modelica source code anymore (issue
  [#11](https://github.com/roskakori/pygount/issues/11)).
- Add detection of DocBook XML by DTD (issue [#10](https://github.com/roskakori/pygount/issues/10)).
- Add support for suffices to indicate PL/SQL files according to [Oracle FAQ entry on file extensions](http://www.orafaq.com/wiki/File_extensions) (issue [#12](https://github.com/roskakori/pygount/issues/12)).
- Add possibility to specify a fallback encoding for encoding 'chardet'. Use e.g. `--encoding=chardet;cp1252`.

## Version 0.8, 2016-10-07

- Fix option `--verbose`. Now each analyzed source code results in at least one informational message in the log.
- Add detection of duplicates using size and then MD5 code as criteria (issue [#2](https://github.com/roskakori/pygount/issues/2)). Use the option `--duplicates` to still count duplicate source code.
- Improve detection of programming language, which is now more consistent and yields the same language between Python invocations.

## Version 0.7, 2016-09-28

- Fix that option `--generated` was ignored.
- Add support for a couple of languages not supported by `pygments` yet:
  - m4, VBScript, and WebFOCUS use minimalistic lexers that can distinguish between comments and code.
  - OMG IDL repurposes the existing Java lexer.
- Add detection of certain XML dialects as separate language (issue [#8](https://github.com/roskakori/pygount/issues/8)).

## Version 0.6, 2016-09-26

- Fix that source files could end up as `__error__` if the first non-ASCII characters showed up only after kilobyte 16 and the encoding was not UTF-8. Now pygount attempts to read the whole file as UTF-8 before assuming it actually is UTF-8.
- Change lines in plain text files to count as comments (issue [#9](https://github.com/roskakori/pygount/issues/9)). Before pygments treated them as `ResourceBundle`.
- Change that empty files have `__empty__` as language (issue [#7](https://github.com/roskakori/pygount/issues/7)).
- Extend workaround for [pygments issue #1284](https://bitbucket.org/birkenfeld/pygments-main/issues/1284) to replace any lexer `*+Evoque` by `*`.

## Version 0.5, 2016-09-22

- Add that generated source code is excluded from analysis (issue [#1](https://github.com/roskakori/pygount/issues/1)). Use option `--generated` to specify patterns that indicate generated code.
- Add workaround for pygments sometimes detecting the same XML file as XML and other times as XML+Evoque (probably depending on the hash seed). Now XML+Evoque is always changed to XML.
- Add `__pycache__` as default `--folders-to-skip`.
- Add notes on pseudo languages for source code that cannot be analyzed.

## Version 0.4, 2016-09-11

- Fixed `LookupError` on broken encoding in magic comment (issue [#4](https://github.com/roskakori/pygount/issues/4)).
- Add options `--folders-to-skip` and `--names-to-skip` to specify which files should be excluded from analysis.
- Add comma (`,`) and colon (`:`) to list of "white characters" that do not count as code if there is nothing else in the line.
- Improve pattern matching: for all options that according to `--help` take `PATTERNS` you can now specify that the patterns are regular expressions instead of shell patterns (using `[regex]`) and that they should extend the default patterns (using `[...]`).
- Improve documentation: added notes on how code is counted and how pygount compares to other similar tools.

## Version 0.3, 2016-08-20

- Fix `@rem` comments in DOS batch files (issue [#3](https://github.com/roskakori/pygount/issues/3)).
- Clean up code.

## Version 0.2, 2016-07-10

- Fix that files starting with underscore (e.g. `__init__.py`) were excluded from analysis.
- Change `chardet` package to be optional.
- Add possibility to specify single files and glob patterns to analyze.
- Add that lines containing only certain characters are treated as white space instead of code. Currently, this concerns brackets (`()[]{}`) and semicolon (`;`).
- Add that Python's `pass` statement is treated as white space instead of code.
- Clean up and (slightly) optimized code.

## Version 0.1, 2016-07-05

- Initial public release.
