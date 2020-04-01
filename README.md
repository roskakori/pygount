![Python Versions](https://img.shields.io/pypi/pyversions/pygount.svg)
![Build Status](https://img.shields.io/github/workflow/status/roskakori/pygount/Build)
[![Test Coverage](https://img.shields.io/coveralls/github/roskakori/pygount)](https://coveralls.io/r/roskakori/pygount?branch=master)
[![License](https://img.shields.io/github/license/roskakori/pygount)](https://opensource.org/licenses/BSD-3-Clause)

# pygount

Pygount is a command line tool to scan folders for source code files and
count the number of source code lines in it. It is similar to tools like
[sloccount](http://www.dwheeler.com/sloccount/) and
[cloc](http://cloc.sourceforge.net/>) but uses the
[pygments](http://pygments.org/)
package to analyze the source code and consequently can analyze any
[programming language supported by pygments](http://pygments.org/languages/).

The name is a combination of pygments and count.

Pygount is open source and distributed under the
[BSD license](https://opensource.org/licenses/BSD-3-Clause>). The source
code is available from https://github.com/roskakori/pygount.


## Quickstart

For installation run

```bash
$ pip install pygount
```

To get a list of line counts for a projects stored in a certain folder run for
example:

```bash
$ pygount ~/projects/exammple
```

To limit the analysis to certain file types identified by their suffix:

```bash
$ pygount --suffix=cfg,py,yml  ~/projects/exammple
```

To get a summary of each programming language with sum counts and percentage:

```bash
$ pygount --format=summary ~/projects/exammple
```

Plenty of tools can post process SLOC information, for example the
[SLOCCount plug-in](https://wiki.jenkins-ci.org/display/JENKINS/SLOCCount+Plugin)
for the [Jenkins](https://jenkins.io/) continuous integration server.

A popular format for such tools is the XML format used by cloc, which pygount
also supports and can store in an output file:

```bash
$ pygount --format=cloc-xml --out=cloc.xml ~/projects/exammple
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
