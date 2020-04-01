API
===

Overview
--------

Pygount provides a simple API to integrate in other tools. This however is
currently still a work in progress and subject to change.

Here's an example on how to analyze one of pygount's own source codes:

.. code-block:: pycon

    >>> import pygount
    >>> pygount.source_analysis('pygount/analysis.py', 'pygount')
    SourceAnalysis(path='pygount/analysis.py', language='Python', group='pygount', state=analyzed, code=464, documentation=108, empty=104, string=22)


Reference
---------

.. automodule:: pygount
    :members:
