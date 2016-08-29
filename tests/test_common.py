"""
Tests for :py:mod:`pygount.common` module.
"""
# Copyright (c) 2016, Thomas Aglassinger.
# All rights reserved. Distributed under the BSD License.
import unittest

import pygount.common


class OptionErrorTest(unittest.TestCase):
    def test_can_build_str(self):
        error_without_source = pygount.common.OptionError('test')
        self.assertEqual(str(error_without_source), 'test')

        error_with_source = pygount.common.OptionError('test', 'some_file.txt')
        self.assertEqual(str(error_with_source), 'some_file.txt: test')


if __name__ == '__main__':
    unittest.main()
