"""
Tests for pygount source code analysis.
"""
# Copyright (c) 2016, Thomas Aglassinger.
# All rights reserved. Distributed under the BSD License.
import unittest

from pygments import token

import pygount.lexers


class IdlLexerTest(unittest.TestCase):
    def test_can_lex_idl(self):
        lexer = pygount.lexers.IdlLexer()
        text = '\n'.join([
            '/* some',
            ' * comment */',
            'module HelloApp {',
            '  interface Hello {',
            '    string sayHello(); // Be friendly!',
            '  };',
            '};',
        ])
        text_tokens = list(lexer.get_tokens(text))
        print(text_tokens)
        self.assertEqual(text_tokens, [
            (token.Token.Comment.Multiline, '/* some\n * comment */'),
            (token.Token.Text, '\n'),
            (token.Token.Name, 'module'),
            (token.Token.Text, ' '),
            (token.Token.Name, 'HelloApp'),
            (token.Token.Text, ' '),
            (token.Token.Operator, '{'),
            (token.Token.Text, '\n'),
            (token.Token.Text, '  '),
            (token.Token.Keyword.Declaration, 'interface'),
            (token.Token.Text, ' '),
            (token.Token.Name.Class, 'Hello'),
            (token.Token.Text, ' '),
            (token.Token.Operator, '{'),
            (token.Token.Text, '\n'),
            (token.Token.Text, '    '),
            (token.Token.Name, 'string'),
            (token.Token.Text, ' '),
            (token.Token.Name.Function, 'sayHello'),
            (token.Token.Operator, '('),
            (token.Token.Operator, ')'),
            (token.Token.Operator, ';'),
            (token.Token.Text, ' '),
            (token.Token.Comment.Single, '// Be friendly!\n'),
            (token.Token.Text, '  '),
            (token.Token.Operator, '}'),
            (token.Token.Operator, ';'),
            (token.Token.Text, '\n'),
            (token.Token.Operator, '}'),
            (token.Token.Operator, ';'),
            (token.Token.Text, '\n'),
        ])


class MinimalisticM4LexerTest(unittest.TestCase):
    def test_can_lex_m4(self):
        lexer = pygount.lexers.MinimalisticM4Lexer()
        text = ''
        text += '#\n'
        text += '# comment\n'
        text += "define(FRUIT, apple) # Healthy stuff!\n"
        text += 'Eat some FRUIT!'
        text_tokens = list(lexer.get_tokens(text))
        self.assertEqual(text_tokens, [
            (token.Token.Comment.Single, '#\n'),
            (token.Token.Comment.Single, '# comment\n'),
            (token.Token.Text, 'define(FRUIT, apple) '),
            (token.Token.Comment.Single, '# Healthy stuff!\n'),
            (token.Token.Text, 'Eat some FRUIT!\n'),
        ])


class MinimalisticVBScriptLexerTest(unittest.TestCase):
    def test_can_lex_vbscript(self):
        lexer = pygount.lexers.MinimalisticVBScriptLexer()
        text = ''
        text += "' comment\n"
        text += 'WScript.Echo "hello world!"'
        text_tokens = list(lexer.get_tokens(text))
        self.assertEqual(text_tokens, [
            (token.Token.Comment.Single, "' comment\n"),
            (token.Token.Text, 'WScript.Echo "hello world!"\n'),
        ])


class MinimalisticWebFocusLexerTest(unittest.TestCase):
    def test_can_lex_webfocus(self):
        lexer = pygount.lexers.MinimalisticWebFocusLexer()
        text = ''
        text += '-*\n'
        text += '-* comment\n'
        text += "-set &some='text';\n"
        text += 'table file some print * end;'
        text_tokens = list(lexer.get_tokens(text))
        self.assertEqual(text_tokens, [
            (token.Token.Comment.Single, '-*\n'),
            (token.Token.Comment.Single, '-* comment\n'),
            (token.Token.Text, "-set &some='text';\n"),
            (token.Token.Text, "table file some print * end;\n"),
        ])


class PlainTextLexerTest(unittest.TestCase):
    def test_can_lex_plain_text(self):
        lexer = pygount.lexers.PlainTextLexer()
        text = ''
        text += 'a\n'  # line with text
        text += '\n'  # empty line
        text += ' \t \n'  # line containing only white space
        text += '  '  # trailing while space line without newline character
        text_tokens = list(lexer.get_tokens(text))
        self.assertEqual(text_tokens, [
            (token.Token.Comment.Single, 'a\n'),
            (token.Token.Text, '\n \t \n  \n')
        ])
