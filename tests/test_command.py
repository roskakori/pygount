"""
Tests for pygount command line interface.
"""
# Copyright (c) 2016, Thomas Aglassinger.
# All rights reserved. Distributed under the BSD License.
import os
import tempfile
import unittest
from xml.etree import ElementTree

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
            self.fail('unknown --encoding must exit')
        except SystemExit as system_exit:
            self.assertEqual(system_exit.code, 2)

    def test_fails_on_unknown_format(self):
        try:
            command.pygount_command(['--format', 'no_such_encoding', tempfile.gettempdir()])
            self.fail('unknown --format must exit')
        except SystemExit as system_exit:
            self.assertEqual(system_exit.code, 2)

    def test_can_analyze_pygount_setup_py(self):
        pygount_setup_py_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'setup.py')
        exit_code = command.pygount_command(['--verbose', pygount_setup_py_path])
        self.assertEqual(exit_code, 0)

    def test_can_analyze_pygount_source_code(self):
        pygount_folder = os.path.dirname(os.path.dirname(__file__))
        exit_code = command.pygount_command(['--verbose', pygount_folder])
        self.assertEqual(exit_code, 0)

    def test_can_analyze_pygount_source_code_as_cloc_xml(self):
        pygount_folder = os.path.dirname(os.path.dirname(__file__))
        cloc_xml_folder = os.path.join(pygount_folder, 'tests', 'temp')
        os.makedirs(cloc_xml_folder, exist_ok=True)
        cloc_xml_path = os.path.join(cloc_xml_folder, 'cloc.xml')
        exit_code = command.pygount_command([
            '--verbose',
            '--format',
            'cloc-xml',
            '--out',
            cloc_xml_path,
            pygount_folder])
        self.assertEqual(exit_code, 0)
        self.assertTrue(os.path.exists(cloc_xml_path))
        cloc_xml_root = ElementTree.parse(cloc_xml_path)
        file_elements = cloc_xml_root.findall('files/file')
        self.assertIsNotNone(file_elements)
        self.assertNotEqual(len(file_elements), 0)
