pygount
=======

Pygount is a command line tool to scan folders for source code files and
count the number of source code lines in it. It is similar to tools like
`sloccount <http://www.dwheeler.com/sloccount/>`_ and
`cloc <http://cloc.sourceforge.net/>`_ but uses the
`pygments <http://pygments.org/>`_
package to analyze the source code and consequently can analyze any
`programming language supported by pygments <http://pygments.org/languages/>`_.

The name is a combination of **pyg**ments and c**ount**.


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
point.

There are a couple of command line options, to find out more, run::

$ pygount --help


Revision history
----------------

Version 0.0.2, 2016-06-13

* Fixed missing reset of chardet analyzer between files.
* Changed default detection of encoding to a lightweight one that recognizes
  BOMs, magic comments, XML prologs and otherwise attempts UTF-8. If that
  fails, use CP1252 and ignore possible encoding errors.
* Added option --encoding the specify the encoding.
* Added option --suffix to specify a comma separated list of suffixes the
  analysis should be limited to, e.g. "py,sql".
* Added filter to exclude "hidden" files and folders from analysis.

Version 0.0.1, 2016-06-08

* Initial internal release.
