"""
Tests for pygount.
"""
import unittest

from pygount import command


class PygountCommandTest(unittest.TestCase):
    def test_can_show_version(self):
        try:
            command.pygount_command(['--help'])
        except SystemExit as system_exit:
            self.assertEqual(system_exit.code, 0)

    def test_can_show_version(self):
        try:
            command.pygount_command(['--version'])
        except SystemExit as system_exit:
            self.assertEqual(system_exit.code, 0)

