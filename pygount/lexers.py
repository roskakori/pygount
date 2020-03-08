"""
Additional lexers for pygount that fill gaps left by :py:mod:`pygments`.
"""
# Copyright (c) 2016-2020, Thomas Aglassinger.
# All rights reserved. Distributed under the BSD License.
import pygments.lexer
import pygments.lexers
import pygments.token
import pygments.util


class IdlLexer(pygments.lexers.JavaLexer):
    """
    Lexer for OMG Interface Definition Language (IDL) that simply uses the
    existing Java lexer to find comments. While this is useless for syntax
    highlighting it is good enough for counting lines.
    """

    name = "IDL"
    filenames = ["*.idl"]


class MinimalisticM4Lexer(pygments.lexer.RegexLexer):
    """
    Minimalistic lexer for m4 macro processor that can distinguish between
    comments and code. It does not recognize a redefined comment mark though.
    """

    name = "M4"
    tokens = {
        "root": [
            (r"(.*)(#.*\n)", pygments.lexer.bygroups(pygments.token.Text, pygments.token.Comment.Single)),
            (r".*\n", pygments.token.Text),
        ]
    }


class MinimalisticVBScriptLexer(pygments.lexer.RegexLexer):
    """
    Minimalistic lexer for VBScript that can distinguish between comments and
    code.
    """

    name = "VBScript"
    tokens = {"root": [(r"\s*'.*\n", pygments.token.Comment.Single), (r".*\n", pygments.token.Text)]}


class MinimalisticWebFocusLexer(pygments.lexer.RegexLexer):
    """
    Minimalistic lexer for WebFOCUS that can distinguish between comments and
    code.
    """

    name = "WebFOCUS"
    tokens = {"root": [(r"-\*.*\n", pygments.token.Comment.Single), (r".*\n", pygments.token.Text)]}


class PlainTextLexer(pygments.lexer.RegexLexer):
    """
    Simple lexer for plain text that treats every line with non white space
    characters as :py:data:`pygments.Token.Comment.Single` and only lines
    that are empty or contain only white space as
    :py:data:`pygments.Token.Text`.

    This way, plaint text files count as documentation.
    """

    name = "Text"
    tokens = {"root": [(r"\s*\n", pygments.token.Text), (r".+\n", pygments.token.Comment.Single)]}
