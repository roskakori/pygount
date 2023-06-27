Background
##########

How pygount counts code
--------------------------

Pygount basically counts physical lines of source code.

First, it lexes the code using the lexers ``pygments`` assigned to it. If
``pygments`` cannot find an appropriate lexer, pygount has a few additional
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
read. Currently white characters are::

    (),:;[]{}

Because of that, pygount reports about 10 to 20 percent fewer SLOC for C-like
languages than other similar tools.

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
-----------------------------------

Pygount can analyze more languages than other common tools such as sloccount
or cloc because it builds on ``pygments``, which provides lexers for hundreds
of languages. This also makes it easy to support another language: simply
`write your own lexer <http://pygments.org/docs/lexerdevelopment/>`_.

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
