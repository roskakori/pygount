# Usage

## General

Run and specify the folder to analyze recursively, for example:

```bash
$ pygount ~/development/sometool
```

If you omit the folder, the current folder of your shell is used as a starting point. Apart from folders you can also specify single files and shell patterns (using `?`, `*` and ranges like `[a-z]`).

Certain files and folders are automatically excluded from the analysis:

- files starting with dot (`.`) or ending in tilda (`~`)
- folders starting with dot (`.`) or named `_svn`.

### `--folders-to-skip LIST`, `--names-to-skip LIST`

To specify alternative patterns, use `--folders-to-skip` and `--names-to-skip`. Both take a comma separated list of patterns, see below on the pattern syntax. To, for example, also prevent folders starting with two underscores (`_`) from being analyzed, specify `--folders-to-skip=[...],__*`.

### `--suffix LIST`

To limit the analysis on certain file types, you can specify a comma separated list of suffixes to take into account, for example `--suffix=py,sql,xml`.

### `--out FILE`

By default, the results of the analysis are written to the standard output. To redirect the output to a file, use for example `--out=counts.txt`.

To explicitly redirect to the standard output specify `--out=STDOUT`.

### `--format FORMAT`

By default, the results of the analysis are written to the standard output in a format similar to sloccount. To redirect the output to a file, use e.g. `--out=counts.txt`. To change the format to an XML file similar to cloc, use `--format=cloc-xml`.

To just get a quick grasp of the languages used in a project and their respective importance use `--format=summary` which provides a language overview and a sum total. For example, pygount's summary looks like this:

```
Language          Files    %     Code    %     Comment    %
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

The summary output is designed for human readers, and the column widths adjust to the data.

For further processing the results of pygount, `--format=json` should be the easiest to deal with. For more information, see the chapter on [JSON](json.md).

### `--merge-embedded-languages`

Some languages such as HTML or JavaScript allow embedding other languages in their source code. In that case, the source code is assigned to a language that contains both the base and end embedded language in its name, for example:

- HTML+Jinja
- JavaScript+Lasso

If you prefer count all variants of a base language only under its own name, specify `--merge-embedded-languages`. The example above will then show as:

- HTML
- JavaScript

Consequently, multiple different embedded languages will all count for its common base language.

## Remote repositories

Additionally to local files, pygount can analyze remote git repositories:

```bash
$ pygount https://github.com/roskakori/pygount.git
```

In the background, this creates a shallow clone of the repository in a temporary folder that after the analysis is removed automatically.

Therefore, you need to have at read access to the repository.

If you want to analyze a specific revision, specify it at the end of the URL:

```bash
$ pygount https://github.com/roskakori/pygount.git/v1.6.0
```

The remote URL supports the git standard protocols: git, HTTP/S and SSH.

```bash
$ pygount git@github.com:username/project.git
```

You can specify multiple repositories, for example, to include both the web application, command line client and docker container of the [Weblate](https://weblate.org/) project:

```bash
$  pygount https://github.com/WeblateOrg/weblate.git https://github.com/WeblateOrg/wlc.git  https://github.com/WeblateOrg/docker.git
```

And you can even mix local files and remote repositories:

```bash
$ pygount ~/projects/some https://github.com/roskakori/pygount.git
```

## Patterns

Some command line arguments take patterns as values.

By default, patterns are shell patterns using `*`, `?` and ranges like `[a-z]` as placeholders. Depending on your platform, they are case-sensitive (Unix) or not (macOS, Windows).

If a pattern starts with `[regex]` you can specify a comma separated list of regular expressions instead using all the constructs supported by the [Python regular expression
syntax](https://docs.python.org/3/library/re.html#regular-expression-syntax). Regular expressions are case-sensitive unless they include a `(?i)` flag.

If the first actual pattern is `[...]`, default patterns are included. Without it, defaults are ignored and only the patterns explicitly stated are taken into account.

### `--generated`

So for example, to specify that generated code can also contain the German word "generiert" in a case-insensitive way use `--generated="[regex][...](?i).*generiert"`.

## Counting duplicates

### `--duplicates`

By default, pygount prevents multiple source files with exactly the same
content to be counted again.

For two files to be considered duplicates, the following conditions must be met:

1.  Both files have the same size.
2.  Both files have the same [SHA-256](https://en.wikipedia.org/wiki/SHA-2) hashcode.

This allows for efficient detection with a tiny possibility for false positives.

However, it also prevents detection of files with only minor differences as duplicates. Examples are files that are identical except for additional white space, empty lines or different line endings.

If you still want to count duplicates multiple times, specify `--duplicates`. This will also result in a minor performance gain of the analysis.

## Source code encoding

### --encoding ENCODING\[;FALLBACK\]

When reading source code, pygount automatically detects the encoding. It uses a simple algorithm where it recognizes BOM, XML declarations such as:

```xml
<?xml encoding='cp1252'?>
```

and "magic" comments such as:

```ruby
# encoding: cp1252
# coding: cp1252
# -*- coding: cp1252 -*-
```

If the file does not have an appropriate heading, pygount attempts to read it using UTF-8. If this fails, it reads the file using a fallback encoding (by default [CP1252](https://en.wikipedia.org/wiki/Windows-1252)) and ignores any encoding errors.

You can change this behavior using the `--encoding` option:

- To keep the automatic analysis and use a different fallback encoding, specify for example `--encoding=automatic;iso-8859-15`.
- To use automatic detection based on heuristic, specify `--encoding=chardet`. For this to work, the [chardet](https://pypi.python.org/pypi/chardet)
  package must be installed,
- To use a specific encoding (for all files analyzed), use for example `--encoding=iso-8859-15`.

## Pseudo languages

If a source code is not counted, the number of lines is 0 and the language shown is a pseudo language indicating the reason:

- `__binary__` - used for `binary`.
- `__duplicate__` - the source code duplicate as described at the
  command line option `--duplicates`.
- `__empty__` - the source code is an empty file with a size of 0 bytes.
- `__error__` - the source code could not be parsed; for example, due to an I/O
  error.
- `__generated__` - the source code is generated according to the
  command line option `--generated`.
- `__unknown__` - pygments does not provide a lexer to parse the source
  code.

## Other information

### `--verbose`

If `--verbose` is specified, pygount logs detailed information about what it is doing.

### `--help`

To get a description of all the available command line options, run:

```bash
$ pygount --help
```

### `--version`

To get pygount's current version number, run:

```bash
$ pygount --version
```
