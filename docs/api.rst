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
    SourceAnalysis(path='pygount/analysis.py', language='Python', group='pygount', code=302, documentation=66, empty=62, string=23, state='analyzed', state_info=None)


Reference
---------

.. automodule:: pygount
    :members:
