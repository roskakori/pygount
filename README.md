[![PyPI](https://img.shields.io/pypi/v/pygount)](https://pypi.org/project/pygount/)
[![Python Versions](https://img.shields.io/pypi/pyversions/pygount.svg)](https://www.python.org/downloads/)
[![Build Status](https://github.com/roskakori/pygount/actions/workflows/build.yml/badge.svg)](https://github.com/roskakori/pygount/actions/workflows/build.yml)
[![Test Coverage](https://img.shields.io/coveralls/github/roskakori/pygount)](https://coveralls.io/r/roskakori/pygount?branch=master)
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
$ pygount --suffix=cfg,py,yml  ~/projects/example
```

To get a summary of each programming language with sum counts and percentage:

```bash
$ pygount --format=summary ~/projects/example
```

As an example here is the summary output for pygount's own source code:

```
    Language      Files    %     Code    %     Comment    %
----------------  -----  ------  ----  ------  -------  ------
Python               19   51.35  1924   72.99      322   86.10
reStructuredText      7   18.92   332   12.59        7    1.87
markdown              3    8.11   327   12.41        1    0.27
Batchfile             1    2.70    24    0.91        1    0.27
YAML                  1    2.70    11    0.42        2    0.53
Makefile              1    2.70     9    0.34        7    1.87
INI                   1    2.70     5    0.19        0    0.00
TOML                  1    2.70     4    0.15        0    0.00
Text                  3    8.11     0    0.00       34    9.09
----------------  -----  ------  ----  ------  -------  ------
Sum total            37          2636              374
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
