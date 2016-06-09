pygount
=======

Pygount is a command line tool to scan folders for source code files and
count the number of source code lines in it. It is similar to tools like
`sloccount <http://www.dwheeler.com/sloccount/>`_ and
`cloc <http://cloc.sourceforge.net/>`_ but uses the
`pygments <http://pygments.org/>`_
package to analyze the source code and
consequently can analyze any
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

$ pygount ~/workspace/sometool

If you omit the folder, the current folder of you shell is used as starting point.

There are a couple of command line options, to find out more, run::

$ pygount --help


Revision history
----------------

Version 0.0.1, 2016-06-08

* Initial internal release.
