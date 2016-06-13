"""
Tests for pygount.
"""
import os
import tempfile
import unittest

from pygount import command


class PygountCommandTest(unittest.TestCase):
    def test_can_show_help(self):
        try:
            command.pygount_command(['--help'])
            self.fail('--help must exit')
        except SystemExit as system_exit:
            self.assertEqual(system_exit.code, 0)

    def test_can_show_version(self):
        try:
            command.pygount_command(['--version'])
            self.fail('--version must exit')
        except SystemExit as system_exit:
            self.assertEqual(system_exit.code, 0)

    def test_fails_on_unknown_encoding(self):
        try:
            command.pygount_command(['--encoding', 'no_such_encoding', tempfile.gettempdir()])
            self.fail('unknown encoding must exit')
        except SystemExit as system_exit:
            self.assertEqual(system_exit.code, 2)

    def test_can_anylyze_pygount_source_code(self):
        pygount_folder = os.path.dirname(os.path.dirname(__file__))
        exit_code= command.pygount_command(['--verbose', pygount_folder])
        self.assertEqual(exit_code, 0)

