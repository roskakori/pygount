.. image:: https://travis-ci.org/roskakori/pygount.svg?branch=master
    :target: https://travis-ci.org/roskakori/pygount
    :alt: Build Status

.. image:: https://coveralls.io/repos/roskakori/pygount/badge.png?branch=master
    :target: https://coveralls.io/r/roskakori/pygount?branch=master
    :alt: Test coverage

.. image:: https://landscape.io/github/roskakori/pygount/master/landscape.svg?style=flat
    :target: https://landscape.io/github/roskakori/pygount/master
    :alt: Code Health


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


Jenkins
-------

Pygount can produce output that can be processed by the
`SLOCCount plug-in <https://wiki.jenkins-ci.org/display/JENKINS/SLOCCount+Plugin>`_
for `Jenkins <https://jenkins.io/>`_ continuous integration server.

Example::

pygount --format=cloc-xml --out cloc.xml --suffix=py --verbose .

Then add a post-build action "Publish SLOCCount analysis results" and set
"SLOCCount report" to "cloc.xml".


Revision history
----------------

Version 0.0.1, 2016-07-05

* Initial public release.
