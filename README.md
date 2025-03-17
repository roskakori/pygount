[![PyPI](https://img.shields.io/pypi/v/pygount)](https://pypi.org/project/pygount/)
[![Python Versions](https://img.shields.io/pypi/pyversions/pygount.svg)](https://www.python.org/downloads/)
[![Build Status](https://github.com/roskakori/pygount/actions/workflows/build.yml/badge.svg)](https://github.com/roskakori/pygount/actions/workflows/build.yml)
[![Test Coverage](https://img.shields.io/coveralls/github/roskakori/pygount)](https://coveralls.io/r/roskakori/pygount?branch=main)
[![Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![License](https://img.shields.io/github/license/roskakori/pygount)](https://opensource.org/licenses/BSD-3-Clause)

# pygount

Pygount is a command line tool to scan folders for source code files and
count the number of source code lines in it. It is similar to tools like
[sloccount](https://www.dwheeler.com/sloccount/) and
[cloc](https://github.com/AlDanial/cloc) but uses the
[pygments](https://pygments.org/)
package to analyze the source code and consequently can analyze any
[programming language supported by pygments](https://pygments.org/languages/).

The name is a combination of pygments and count.

Pygount is open source and distributed under the
[BSD license](https://opensource.org/licenses/BSD-3-Clause). The source
code is available from https://github.com/roskakori/pygount.

## Quickstart

For installation run

```bash
$ pip install pygount
```

To get a list of line counts for a projects stored in a certain folder run for
example:

```bash
$ pygount ~/projects/example
```

To limit the analysis to certain file types identified by their suffix:

```bash
$ pygount --suffix=cfg,py,yml ~/projects/example
```

To get a summary of each programming language with sum counts and percentage:

```bash
$ pygount --format=summary ~/projects/example
```

To analyze a remote git repository directly without having to clone it first:

```bash
$ pygount --format=summary https://github.com/roskakori/pygount.git
```

You can pass a specific revision at the end of the remote URL:

```bash
$ pygount --format=summary https://github.com/roskakori/pygount.git/v1.5.1
```

This example results in the following summary output:

```
┏━━━━━━━━━━━━━━━━━━┳━━━━━━━┳━━━━━━━┳━━━━━━┳━━━━━━┳━━━━━━━━━┳━━━━━━┓
┃ Language         ┃ Files ┃     % ┃ Code ┃    % ┃ Comment ┃    % ┃
┡━━━━━━━━━━━━━━━━━━╇━━━━━━━╇━━━━━━━╇━━━━━━╇━━━━━━╇━━━━━━━━━╇━━━━━━┩
│ Python           │    21 │  48.8 │ 2414 │ 63.4 │     436 │ 11.4 │
│ TOML             │     1 │   2.3 │   46 │ 23.1 │      38 │ 19.1 │
│ Batchfile        │     1 │   2.3 │   24 │ 68.6 │       1 │  2.9 │
│ Bash             │     4 │   9.3 │   20 │ 60.6 │      13 │ 39.4 │
│ Makefile         │     1 │   2.3 │    9 │ 45.0 │       7 │ 35.0 │
│ reStructuredText │     9 │  20.9 │    0 │  0.0 │     538 │ 49.6 │
│ Markdown         │     3 │   7.0 │    0 │  0.0 │      57 │ 47.1 │
│ Text only        │     2 │   4.7 │    0 │  0.0 │      23 │ 82.1 │
│ __unknown__      │     1 │   2.3 │    0 │  0.0 │       0 │  0.0 │
├──────────────────┼───────┼───────┼──────┼──────┼─────────┼──────┤
│ Sum              │    43 │ 100.0 │ 2513 │ 47.1 │    1113 │ 20.9 │
└──────────────────┴───────┴───────┴──────┴──────┴─────────┴──────┘
```

Plenty of tools can post process SLOC information, for example the
[SLOCCount plug-in](https://wiki.jenkins-ci.org/display/JENKINS/SLOCCount+Plugin)
for the [Jenkins](https://jenkins.io/) continuous integration server.

A popular format for such tools is the XML format used by cloc, which pygount
also supports and can store in an output file:

```bash
$ pygount --format=cloc-xml --out=cloc.xml ~/projects/example
```

To get a short description of all available command line options use:

```bash
$ pygount --help
```

For more information and examples read the documentation chapter on
[Usage](https://pygount.readthedocs.io/en/latest/usage.html).

## Contributions

To report bugs, visit the
[issue tracker](https://github.com/roskakori/pygount/issues).

In case you want to play with the source code or contribute improvements, see
[CONTRIBUTING](https://pygount.readthedocs.io/en/latest/contributing.html).

## Version history

See [CHANGES](https://pygount.readthedocs.io/en/latest/changes.html).
