"""
Tests for pygount.
"""
# Copyright (c) 2016, Thomas Aglassinger.
# All rights reserved. Distributed under the BSD License.
import atexit
import os
import tempfile
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

    def test_can_convert_python_strings_to_comments(self):
        source_code = \
            '#!/bin/python\n' \
            '"Some tool."\n' \
            '#(C) by me\n' \
            'def x():\n' \
            '    "Some function"\n' \
            '    return 1'
        python_lexer = lexers.get_lexer_by_name('python')
        python_tokens = python_lexer.get_tokens(source_code)
        for token_type, token_text in list(analysis._pythonized_comments(analysis._delined_tokens(python_tokens))):
            self.assertNotIn(token_type, token.String, 'token_text=%r' % token_text)


class EncodingTest(unittest.TestCase):
    _ENCODING_TO_BOM_MAP = dict((encoding, bom) for bom, encoding in analysis._BOM_TO_ENCODING_MAP.items())
    _TEST_CODE =  "x = '\u00fd \u20ac'"

    def _test_path(self, name):
        result = os.path.join(tempfile.gettempdir(), 'pygount_tests_EncodingTest_' + name + '.tmp')
        atexit.register(os.remove, result)
        return result

    def _test_can_detect_bom_encoding(self, encoding):
        test_path = self._test_path(encoding)
        with open(test_path, 'wb') as test_file:
            if encoding != 'utf-8-sig':
                bom = EncodingTest._ENCODING_TO_BOM_MAP[encoding]
                test_file.write(bom)
            test_file.write(EncodingTest._TEST_CODE.encode(encoding))
        actual_encoding = analysis.encoding_for(test_path)
        self.assertEqual(actual_encoding, encoding)

    def test_can_detect_bom_encodings(self):
        for _, encoding in analysis._BOM_TO_ENCODING_MAP.items():
            self._test_can_detect_bom_encoding(encoding)

    def test_can_detect_plain_encoding(self):
        for encoding in ('cp1252', 'utf-8'):
            test_path = self._test_path(encoding)
            with open(test_path, 'w', encoding=encoding) as test_file:
                test_file.write(EncodingTest._TEST_CODE)
        actual_encoding = analysis.encoding_for(test_path)
        self.assertEqual(actual_encoding, encoding)

    def test_can_detect_xml_prolog(self):
        encoding = 'iso-8859-15'
        test_path = self._test_path('xml-' + encoding)
        with open(test_path, 'w', encoding=encoding) as test_file:
            xml_code = '<?xml encoding="{0}" standalone="yes"?><some>{1}</some>'.format(
                encoding, EncodingTest._TEST_CODE)
            test_file.write(xml_code)
        actual_encoding = analysis.encoding_for(test_path)
        self.assertEqual(actual_encoding, encoding)

    def test_can_detect_magic_comment(self):
        encoding = 'iso-8859-15'
        test_path = self._test_path('magic-' + encoding)
        with open(test_path, 'w', encoding=encoding) as test_file:
            test_file.write('#!/usr/bin/python\n')
            test_file.write('# -*- coding: {0} -*-\n'.format(encoding))
            test_file.write(EncodingTest._TEST_CODE)
        actual_encoding = analysis.encoding_for(test_path)
        self.assertEqual(actual_encoding, encoding)

