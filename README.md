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


## Download and installation

Pygount is available from [PyPI](https://pypi.python.org/pypi/pygount) and can
be installed by running:

```bash
$ pip install pygount
```


## Usage

Simply run and specify the folder to analyze recursively, for example:

```bash
$ pygount ~/development/sometool
```

If you omit the folder, the current folder of your shell is used as starting
point. Apart from folders you can also specify single files and shell patterns
(using `?`, `*` and ranges like `[a-z]`).

Certain files and folders are automatically excluded from the analysis:

* files starting with dot (`.`) or ending in tilda (`~`)
* folders starting with dot (`.`) or named `_svn`.

To specify alternative patterns, use `--folders-to-skip` and
`--names-to-skip`. Both take a comma separated list of patterns, see below
on the pattern syntax. To for example also prevent folders starting with two
underscores (`_`) from being analyzed, specify
`--folders-to-skip=[...],__*`.

To limit the analysis on certain file types, you can specify a comma separated
list of suffixes to take into account, for example `--suffix=py,sql,xml`.

By default the result of the analysis are written to the standard output in a
format similar to sloccount. To redirect the output to a file, use e.g.
`--out=counts.txt`. To change the format to an XML file similar to cloc, use
`--format=cloc-xml`.

To just get a quick grasp of the languages used in a project and their
respective importance use `--format=summary` which provides a language
overview and a sum total. For example pygount's summary looks like this:

```bash
    Language      Code    %     Comment    %
----------------  ----  ------  -------  ------
Python            1730   83.94      250   78.12
reStructuredText   271   13.15        0    0.00
Ant                 38    1.84        1    0.31
INI                 10    0.49        1    0.31
Bash                 8    0.39        2    0.62
TOML                 4    0.19        0    0.00
Text                 0    0.00       66   20.62
----------------  ----  ------  -------  ------
Sum total         2061              320
```

The summary output is designed for human readers and the column widths adjust
to the data.


## Patterns

Some command line arguments take patterns as values.

By default, patterns are shell patterns using `*`, `?` and ranges like
`[a-z]` as placeholders. Depending on your platform, the are case sensitive
(Unix) or not (Mac OS, Windows).

If a pattern starts with `[regex]` you can specify a comma separated list
of regular expressions instead using all the constructs supported by the
[Python regular expression syntax](https://docs.python.org/3/library/re.html#regular-expression-syntax).
Regular expressions are case sensitive unless they include a `(?i)` flag.

If the first actual pattern is `[...]`, default patterns are included.
Without it, defaults are ignored and only the pattern explicitly stated are
taken into account.

So for example to specify that generated code can also contain the German word
"generiert" in a case insensivie way use
`--generated="[regex][...](?i).*generiert"`.


## Source code encoding

When reading source code, pygount automatically detects the encoding. It uses
a simple algorithm where it recognizes BOM, XML declarations such as:

```
<?xml encoding='cp1252'?>
```

and "magic" comments such as:

```python
# -*- coding: cp1252 -*-
```

If the file does not have an appropriate heading, pygount attempts to read it
using UTF-8. If this fails, it reads the file using a fallback encoding (by
default CP1252) and ignores any encoding errors.

You can change this behavior using the `--encoding` option:

* To keep the automatic analysis and use a different fallback encoding specify
  for example `--encoding=automatic;iso-8859-15`.
* To use an automatic detection based on heuristic, use
  `--encoding=chardet`. For this to work, the
  `chardet <https://pypi.python.org/pypi/chardet>`_ package must be installed,
* To use a specific encoding (for all files analyzed), use for example
  `--encoding=iso-8859-15`.


## Pseudo languages

If a source code is not counted, the number of lines is 0 and the language
shown is a pseudo language indicating the reason:

* `__binary__` - the source code is a binary file; the detection of binary files
  first ensures that file does not start with a BOM for UTF-8, UTF-16 or
  UTF-32 (which indicates text files). After that it checks for zero bytes
  within the initial 8192 bytes of the file.
* `__duplicate__` - the source code is a bytewise identical copy of another
  file; enable the command line option `--duplicates` to also count code in
  duplicates (and gain a minor performance improvement).
* `__empty__` - the source code is an empty file with a size of 0 bytes.
* `__error__` - the source code could not be parsed e.g. due to an I/O error.
* `__generated__` - the source code is generated according to the command line
  option `--generated`.
* `__unknown__` - pygments does not provide a lexer to parse the source code.


## Other information

To get a description of all the available command line options, run:

```bash
$ pygount --help
```

To get the version number, run:

```bash
$ pygount --version

```


## Continuous integration

Pygount can produce output that can be processed by the
[SLOCCount plug-in](https://wiki.jenkins-ci.org/display/JENKINS/SLOCCount+Plugin)
for the [Jenkins](https://jenkins.io/) continuous integration server.

It's recommended to run pygount as one of the first steps in your build
process before any undesired file like compiler targets or generated source
code are built.

An example "Execute shell" build step for Jenkins is:

```
$ pygount --format=cloc-xml --out cloc.xml --suffix=py --verbose
```

Then add a post-build action "Publish SLOCCount analysis results" and set
"SLOCCount report" to "cloc.xml".


## How pygount counts code

Pygount basically counts physical lines of source code.

First, it lexes the code using the lexers `pygments` assigned to it. If
`pygments` cannot find an appropriate lexer, pygount has a few additional
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
read. Currently white characters are:

```
(),:;[]{}
```

Because of that, pygount reports about 10 to 20 percent fewer SLOC for C-like
languages than other similar tools.

For some languages "no operations" are detected and treated as white space.
For example Python's `pass` or Transact-SQL's `begin` and `end` .

As example consider this Python code:

````python
class SomeError(Exception):
    """
    Some error caused by some issue.
    """
    pass
````

This counts as 1 line of code and 3 lines of comments. The line with `pass`
is considered a "no operation" and thus not taken into account.


## Comparison with other tools

Pygount can analyze more languages than other common tools such as sloccount
or cloc because it builds on `pygments`, which provides lexers for hundreds
of languages. This also makes it easy to support another language: simply
[write your own lexer](http://pygments.org/docs/lexerdevelopment/).

For certain corner cases pygount gives more accurate results because it
actually lexes the code unlike other tools that mostly look for comment
markers and can get confused when they show up inside strings. In practice
though this should not make much of a difference.

Pygount is slower than most other tools. Partially this is due to actually
lexing instead of just scanning the code. Partially other tools can use
statically compiled languages such as Java or C, which are generally faster
than dynamic languages. For many applications though pygount should be
"fast enough", especially when running as an asynchronous step during a
continuous integration build.


## API

Pygount provides a simple API to integrate in other tools. This however is
currently still a work in progress and subject to change.

Here's an example on how to analyze one of pygount's own source codes:

```
>>> import pygount
>>> pygount.source_analysis('pygount/analysis.py', 'pygount')
SourceAnalysis(path='pygount/analysis.py', language='Python', group='pygount', code=302, documentation=66, empty=62, string=23, state='analyzed', state_info=None)
```


## Contributions

In case you want to play with the source code or contribute improvements, see
[CONTRIBUTING](CONTRIBUTING.md).


## Version history

See [CHANGES](CHANGES.md).
