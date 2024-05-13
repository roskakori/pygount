Background
##########

.. _How to count code:

How pygount counts code
-----------------------

Pygount primarily counts the physical lines of source code. It begins by using
lexers from Pygments, if available. If Pygments doesn't have a suitable lexer,
pygount employs its own internal lexers to differentiate between code and
comments. These include:

- Minimalist lexers for m4, VBScript, and WebFOCUS, capable of distinguishing between comments and code.
- The Java lexer repurposed for OMG IDL.

Additionally, plain text is treated with a separate lexer that considers all lines as comments.

Lines consisting solely of comment tokens or whitespace are counted as comments.

Lines with only whitespace are ignored.

All other content is considered code.

White characters
----------------

A line containing only "white characters" is also ignored because the do not
contribute to code complexity in any meaningful way. Currently white
characters are::

    (),:;[]{}

Because of that, pygount tends to report about 5 to 15 percent fewer SLOC for
C-like languages than other similar tools.

.. _No operations:

No operations
-------------

For some languages "no operations" are detected and treated as white space.
For example Python's ``pass`` or Transact-SQL's ``begin`` and ``end`` .

As example consider this Python code:

.. code-block:: python

    class SomeError(Exception):
        """
        Some error caused by some issue.
        """
        pass

This counts as 1 line of code and 3 lines of comments. The line with ``pass``
is considered a "no operation" and thus not taken into account.

.. _Pure string lines:

Pure string lines
-----------------

Many programming languages support the concept of strings, which typically
often contain text to be shown to the end user or simple constant values.
Similar to white character and "no operations", in most cases they do not
add much to the complexity of the code. Notable exceptions are strings
containing code for domain specific languages, templates or SQL statements.

Pygount currently takes an opinionated approach on how to count pure string
lines depending on the output format:

- With ``--format=summary``, pure string lines are ignored similar to empty lines
- With ``--format`` set to ``sloccount`` or ``cloc-xml`` string lines are counted
  as code, resulting in somewhat similar counts as the original tools.
- With ``format=json`` all variants are available as attributes and you can choose
  which one you prefer.

In hindsight, this is an inconsistency that might warrant a cleanup. See issue
`#122 <https://github.com/roskakori/pygount/issues/122>`_ for a discussion and
issue `#152 <https://github.com/roskakori/pygount/issues/152>`_ for a plan on
how to clean this up.

.. _binary:

Binary files
------------

When a file is considered to be binary when all of the following conditions
match:

1. The file does not start with a BOM for UTF-8, UTF-16 or UTF-32 (which
   indicates text files).
2. The initial 8192 bytes contain at least one 0 byte.

In this case, pygount assigns it the pseudo language ``__binary__`` and
performs no further analysis.


Comparison with other tools
---------------------------

Pygount can analyze more languages than other common tools such as sloccount
or cloc because it builds on ``pygments``, which provides lexers for hundreds
of languages. This also makes it easy to support another language: Just
`write your own lexer <http://pygments.org/docs/lexerdevelopment/>`_.

For certain corner cases pygount gives more accurate results because it
actually lexes the code unlike other tools that mostly look for comment
markers and can get confused when they show up inside strings. In practice
though this should not make much of a difference.

Pygount is slower than most other tools. Partially, this is due to actually
lexing instead of just scanning the code. Partially, because other tools can
use statically compiled languages such as Java or C, which are generally
faster than dynamic languages. For many applications though pygount should be
"fast enough", especially when running as an asynchronous step during a
continuous integration build.
