"""
Tests for :py:mod:`pygount.common` module.
"""
# Copyright (c) 2016, Thomas Aglassinger.
# All rights reserved. Distributed under the BSD License.
import re
import unittest

import pygount.common


class OptionErrorTest(unittest.TestCase):
    def test_can_build_str(self):
        error_without_source = pygount.common.OptionError('test')
        self.assertEqual(str(error_without_source), 'test')

        error_with_source = pygount.common.OptionError('test', 'some_file.txt')
        self.assertEqual(str(error_with_source), 'some_file.txt: test')


class RegexFromTest(unittest.TestCase):
    def test_can_match_from_regex(self):
        regex = pygount.common.regex_from(re.compile(r'a\d+b'))
        self.assertRegex('a123b', regex)
        self.assertNotRegex('ab', regex)

    def test_can_match_from_regex_pattern(self):
        regex = pygount.common.regex_from(r'a\d+b')
        self.assertRegex('a123b', regex)
        self.assertNotRegex('ab', regex)

    def test_can_match_from_shell_pattern(self):
        regex = pygount.common.regex_from('*a[0-9]?*b*', True)
        self.assertRegex('a123b', regex)
        self.assertNotRegex('ab', regex)


class RegExesFromTest(unittest.TestCase):
    def test_can_match_single_regex_from_shell_pattern(self):
        regexes = pygount.common.regexes_from('*.py')
        self.assertEqual(len(regexes), 1)
        self.assertRegex('some.py', regexes[0])
        self.assertNotRegex('some.bat', regexes[0])

    def test_can_match_single_regex(self):
        regexes = pygount.common.regexes_from(pygount.common.REGEX_PATTERN_PREFIX + r'^.+\.py$')
        self.assertEqual(len(regexes), 1)
        self.assertRegex('some.py', regexes[0])
        self.assertNotRegex('some.bat', regexes[0])

    def test_can_match_regex_from_multiple_regex_patterns(self):
        regexes = pygount.common.regexes_from(pygount.common.REGEX_PATTERN_PREFIX + r'x, abc, ^.+\.py$')
        self.assertEqual(len(regexes), 3)
        self.assertNotRegex('some.py', regexes[0])
        self.assertNotRegex('some.py', regexes[1])
        self.assertRegex('some.py', regexes[2])

    def test_can_match_regex_from_multiple_default_shell_patterns(self):
        regexes = pygount.common.regexes_from(
            pygount.common.REGEX_PATTERN_PREFIX + pygount.common.ADDITIONAL_PATTERN + r'x',
            'abc, *.py')
        self.assertEqual(len(regexes), 3)
        self.assertNotRegex('some.py', regexes[0])
        self.assertNotRegex('some.py', regexes[1])
        self.assertRegex('some.py', regexes[2])
        self.assertRegex('x', regexes[0])


class AsListTest(unittest.TestCase):
    def test_can_represent_text_as_list(self):
        self.assertEqual(pygount.common.as_list(''), [])
        self.assertEqual(pygount.common.as_list('a'), ['a'])
        self.assertEqual(pygount.common.as_list('abc,d, e'), ['abc', 'd', 'e'])
        self.assertEqual(pygount.common.as_list(',,,,'), [])

    def test_can_represent_iterable_as_list(self):
        self.assertEqual(pygount.common.as_list([]), [])
        self.assertEqual(pygount.common.as_list(['a', 1, None]), ['a', 1, None])
        self.assertEqual(pygount.common.as_list(tuple()), [])
        self.assertEqual(pygount.common.as_list(range(3)), [0, 1, 2])


if __name__ == '__main__':
    unittest.main()
