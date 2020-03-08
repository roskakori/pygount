"""
Tests for additional lexers for pygount.
"""
# Copyright (c) 2016-2020, Thomas Aglassinger.
# All rights reserved. Distributed under the BSD License.

from pygments import token

import pygount.lexers


def test_can_lex_idl():
    lexer = pygount.lexers.IdlLexer()
    text = "\n".join(
        [
            "/* some",
            " * comment */",
            "module HelloApp {",
            "  interface Hello {",
            "    string sayHello(); // Be friendly!",
            "  };",
            "};",
        ]
    )
    text_tokens = list(lexer.get_tokens(text))
    print(text_tokens)
    assert text_tokens == [
        (token.Token.Comment.Multiline, "/* some\n * comment */"),
        (token.Token.Text, "\n"),
        (token.Token.Name, "module"),
        (token.Token.Text, " "),
        (token.Token.Name, "HelloApp"),
        (token.Token.Text, " "),
        (token.Token.Punctuation, "{"),
        (token.Token.Text, "\n"),
        (token.Token.Text, "  "),
        (token.Token.Keyword.Declaration, "interface"),
        (token.Token.Text, " "),
        (token.Token.Name.Class, "Hello"),
        (token.Token.Text, " "),
        (token.Token.Punctuation, "{"),
        (token.Token.Text, "\n"),
        (token.Token.Text, "    "),
        (token.Token.Name, "string"),
        (token.Token.Text, " "),
        (token.Token.Name.Function, "sayHello"),
        (token.Token.Punctuation, "("),
        (token.Token.Punctuation, ")"),
        (token.Token.Punctuation, ";"),
        (token.Token.Text, " "),
        (token.Token.Comment.Single, "// Be friendly!\n"),
        (token.Token.Text, "  "),
        (token.Token.Punctuation, "}"),
        (token.Token.Punctuation, ";"),
        (token.Token.Text, "\n"),
        (token.Token.Punctuation, "}"),
        (token.Token.Punctuation, ";"),
        (token.Token.Text, "\n"),
    ]


def test_can_lex_m4():
    lexer = pygount.lexers.MinimalisticM4Lexer()
    text = ""
    text += "#\n"
    text += "# comment\n"
    text += "define(FRUIT, apple) # Healthy stuff!\n"
    text += "Eat some FRUIT!"
    text_tokens = list(lexer.get_tokens(text))
    assert text_tokens == [
        (token.Token.Comment.Single, "#\n"),
        (token.Token.Comment.Single, "# comment\n"),
        (token.Token.Text, "define(FRUIT, apple) "),
        (token.Token.Comment.Single, "# Healthy stuff!\n"),
        (token.Token.Text, "Eat some FRUIT!\n"),
    ]


def test_can_lex_vbscript():
    lexer = pygount.lexers.MinimalisticVBScriptLexer()
    text = "".join(["' comment\n", 'WScript.Echo "hello world!"'])
    text_tokens = list(lexer.get_tokens(text))
    assert text_tokens == [
        (token.Token.Comment.Single, "' comment\n"),
        (token.Token.Text, 'WScript.Echo "hello world!"\n'),
    ]


def test_can_lex_webfocus():
    lexer = pygount.lexers.MinimalisticWebFocusLexer()
    text = "".join(["-*\n", "-* comment\n", "-set &some='text';\n", "table file some print * end;"])
    text_tokens = list(lexer.get_tokens(text))
    assert text_tokens == [
        (token.Token.Comment.Single, "-*\n"),
        (token.Token.Comment.Single, "-* comment\n"),
        (token.Token.Text, "-set &some='text';\n"),
        (token.Token.Text, "table file some print * end;\n"),
    ]


def test_can_lex_plain_text():
    lexer = pygount.lexers.PlainTextLexer()
    text = "".join(
        [
            "a\n",  # line with text
            "\n",  # empty line
            " \t \n",  # line containing only white space
            "  ",  # trailing while space line without newline character
        ]
    )
    text_tokens = list(lexer.get_tokens(text))
    assert text_tokens == [(token.Token.Comment.Single, "a\n"), (token.Token.Text, "\n \t \n  \n")]
