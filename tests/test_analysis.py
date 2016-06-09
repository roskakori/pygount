"""
Tests for pygount.
"""
import unittest

from pygments import lexers, token

from pygount import analysis


class AnalysisTest(unittest.TestCase):
    def test_can_deline_tokens(self):
        self.assertEqual(
            list(analysis._delined_tokens([(token.Comment, '# a')])),
            [(token.Comment, '# a')]
        )
        self.assertEqual(
            list(analysis._delined_tokens([(token.Comment, '# a\n#  b')])),
            [(token.Comment, '# a\n'), (token.Comment, '#  b')]
        )
        self.assertEqual(
            list(analysis._delined_tokens([(token.Comment, '# a\n#  b\n')])),
            [(token.Comment, '# a\n'), (token.Comment, '#  b\n')]
        )
        self.assertEqual(
            list(analysis._delined_tokens([(token.Comment, '# a\n#  b\n # c\n')])),
            [(token.Comment, '# a\n'), (token.Comment, '#  b\n'), (token.Comment, ' # c\n')]
        )

    def test_can_compute_python_line_parts(self):
        python_lexer = lexers.get_lexer_by_name('python')
        self.assertEqual(
            list(analysis._line_parts(python_lexer, '#')),
            [set('d')]
        )
        self.assertEqual(
            list(analysis._line_parts(python_lexer, "s = 'x'  # x")),
            [set('cds')]
        )
