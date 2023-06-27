API
###

Overview
--------

Pygount provides a simple API to integrate in other tools. This however is
currently still a work in progress and subject to change.

Here's an example on how to analyze one of pygount's own source codes:

.. code-block:: pycon

    >>> from pygount import SourceAnalysis
    >>> SourceAnalysis.from_file("pygount/analysis.py", "pygount")
    SourceAnalysis(path='pygount/analysis.py', language='Python', group='pygount', state=analyzed, code_count=509, documentation_count=141, empty_count=117, string_count=23)

Information about multiple source files can be summarize using
:py:class:`ProjectSummary`:

First, set up the summary:

.. code-block:: pycon

    >>> from pygount import ProjectSummary
    >>> project_summary = ProjectSummary()

Next, find some files to analyze:

.. code-block:: pycon

    >>> from glob import glob
    >>> source_paths = glob("pygount/*.py") + glob("*.md")
    >>> source_paths
    ['pygount/command.py', 'pygount/analysis.py', 'pygount/write.py', 'pygount/__init__.py', 'pygount/xmldialect.py', 'pygount/summary.py', 'pygount/common.py', 'pygount/lexers.py', 'README.md', 'CONTRIBUTING.md', 'CHANGES.md']

Then analyze them:

.. code-block:: pycon

    >>> for source_path in source_paths:
    ...     source_analysis = SourceAnalysis.from_file(source_path, "pygount")
    ...     project_summary.add(source_analysis)

Finally, take a look at the information collected, for example by printing the values of
:py:attr:`ProjectSummary.language_to_language_summary_map`

    >>> for language_summary in project_summary.language_to_language_summary_map.values():
    ...   print(language_summary)
    ...
    LanguageSummary(language='Python', file_count=8, code=1232, documentation=295, empty=331, string=84)
    LanguageSummary(language='markdown', file_count=3, code=64, documentation=0, empty=29, string=14)


Reference
---------

.. automodule:: pygount
    :members:
