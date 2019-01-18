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
from pygount.command import Command
from pygount.common import OptionError


class _BaseCommandTest(unittest.TestCase):
    def setUp(self):
        self.pygount_folder = os.path.dirname(os.path.dirname(__file__))
        self.tests_temp_folder = os.path.join(self.pygount_folder, 'tests', '.temp')
        os.makedirs(self.tests_temp_folder, exist_ok=True)


class CommandTest(_BaseCommandTest):
    def test_fails_on_unknown_output_format(self):
        unknown_output_format = 'no_such_output_format'
        command = Command()
        self.assertRaisesRegex(
            OptionError,
            unknown_output_format,
            command.set_output_format,
            unknown_output_format)

    def test_can_set_encoding(self):
        command = Command()
        command.set_encodings('automatic;cp1252')
        self.assertEqual(command.default_encoding, 'automatic')
        self.assertEqual(command.fallback_encoding, 'cp1252')

    def test_can_execute_on_own_code(self):
        output_path = os.path.join(self.tests_temp_folder, 'test_can_execute_on_own_code.txt')
        try:
            os.remove(output_path)
        except FileNotFoundError:
            pass  # Ignore missing file as it is going to be recreated.
        command = Command()
        command.set_output(output_path)
        command.set_output_format('cloc-xml')
        command.set_source_patterns(self.pygount_folder)
        command.set_suffixes('py')
        command.execute()
        cloc_xml_root = ElementTree.parse(output_path)
        file_elements = cloc_xml_root.findall('files/file')
        self.assertIsNotNone(file_elements)
        self.assertNotEqual(len(file_elements), 0)

    def test_fails_on_broken_regex(self):
        command = Command()
        self.assertRaisesRegex(
            OptionError,
            r'^option --generated: cannot parse pattern for regular repression.*',
            command.set_generated_regexps, '[regex](', 'option --generated'
        )

    def test_can_use_chardet_for_encoding(self):
        command = Command()
        command.set_encodings('chardet')
        command.set_source_patterns(self.pygount_folder)
        command.execute()


class PygountCommandTest(_BaseCommandTest):
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

    def test_fails_on_broken_regex_pattern(self):
        exit_code = command.pygount_command(['--generated', '[regex](', tempfile.gettempdir()])
        self.assertEqual(exit_code, 1)

    def test_can_analyze_pygount_setup_py(self):
        pygount_setup_py_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'setup.py')
        exit_code = command.pygount_command(['--verbose', pygount_setup_py_path])
        self.assertEqual(exit_code, 0)

    def test_can_analyze_pygount_source_code(self):
        pygount_folder = os.path.dirname(os.path.dirname(__file__))
        exit_code = command.pygount_command(['--verbose', pygount_folder])
        self.assertEqual(exit_code, 0)

    def test_can_detect_generated_code(self):
        generated_code_path = os.path.join(self.tests_temp_folder, 'generated.py')
        with open(generated_code_path, 'w', encoding='utf-8') as generated_code_file:
            generated_code_file.write(
                '# Generated with pygount.test_command.PygountCommandTest.test_can_detect_generated_code.\n')
            generated_code_file.write('# Do not edit!\n')
            generated_code_file.write("print('hello World'\n")
        cloc_xml_path = os.path.join(self.tests_temp_folder, 'cloc.xml')
        exit_code = command.pygount_command([
            '--verbose',
            '--format',
            'cloc-xml',
            '--out',
            cloc_xml_path,
            generated_code_path])
        self.assertEqual(exit_code, 0)
        self.assertTrue(os.path.exists(cloc_xml_path))
        cloc_xml_root = ElementTree.parse(cloc_xml_path)
        file_elements = cloc_xml_root.findall("files/file[@language='__generated__']")
        self.assertIsNotNone(file_elements)
        self.assertNotEqual(len(file_elements), 0)

    def test_can_detect_generated_code_with_own_pattern(self):
        generiert_py_path = os.path.join(self.tests_temp_folder, 'generiert.py')
        with open(generiert_py_path, 'w', encoding='utf-8') as generiert_py_file:
            generiert_py_file.write(
                '# Generiert mit pygount.test_command.PygountCommandTest.'
                'test_can_detect_generated_code_with_own_pattern.\n')
            generiert_py_file.write("print('hello World'\n")
        cloc_xml_path = os.path.join(self.tests_temp_folder, 'cloc.xml')
        exit_code = command.pygount_command([
            '--verbose',
            '--format=cloc-xml',
            '--generated=[regex](?i).*generiert',
            '--out',
            cloc_xml_path,
            generiert_py_path])
        self.assertEqual(exit_code, 0)
        self.assertTrue(os.path.exists(cloc_xml_path))
        cloc_xml_root = ElementTree.parse(cloc_xml_path)
        file_elements = cloc_xml_root.findall("files/file[@language='__generated__']")
        self.assertIsNotNone(file_elements)
        self.assertNotEqual(len(file_elements), 0)

    def test_can_analyze_pygount_source_code_as_cloc_xml(self):
        pygount_folder = os.path.dirname(os.path.dirname(__file__))
        cloc_xml_path = os.path.join(self.tests_temp_folder, 'cloc.xml')
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

    def test_can_detect_duplicates(self):
        source_code = "# Duplicate source\nprint('duplicate code')\n"
        original_path = os.path.join(self.tests_temp_folder, 'original.py')
        with open(original_path, 'w') as original_file:
            original_file.write(source_code)
        duplicate_path = os.path.join(self.tests_temp_folder, 'duplicate.py')
        with open(duplicate_path, 'w') as duplicate_file:
            duplicate_file.write(source_code)
        cloc_xml_path = os.path.join(self.tests_temp_folder, 'cloc.xml')
        exit_code = command.pygount_command([
            '--verbose',
            '--format',
            'cloc-xml',
            '--out',
            cloc_xml_path,
            original_path,
            duplicate_path
        ])
        self.assertEqual(exit_code, 0)
        self.assertTrue(os.path.exists(cloc_xml_path))
        cloc_xml_root = ElementTree.parse(cloc_xml_path)
        file_elements = cloc_xml_root.findall("files/file[@language='__duplicate__']")
        self.assertIsNotNone(file_elements)
        self.assertEqual(len(file_elements), 1)

    def test_can_accept_duplicates(self):
        source_code = "# Duplicate source\nprint('duplicate code')\n"
        original_path = os.path.join(self.tests_temp_folder, 'original.py')
        with open(original_path, 'w') as original_file:
            original_file.write(source_code)
        duplicate_path = os.path.join(self.tests_temp_folder, 'duplicate.py')
        with open(duplicate_path, 'w') as duplicate_file:
            duplicate_file.write(source_code)
        cloc_xml_path = os.path.join(self.tests_temp_folder, 'cloc.xml')
        exit_code = command.pygount_command([
            '--duplicates',
            '--verbose',
            '--format',
            'cloc-xml',
            '--out',
            cloc_xml_path,
            original_path,
            duplicate_path
        ])
        self.assertEqual(exit_code, 0)
        self.assertTrue(os.path.exists(cloc_xml_path))
        cloc_xml_root = ElementTree.parse(cloc_xml_path)
        file_elements = cloc_xml_root.findall("files/file[@language='__duplicate__']")
        self.assertIsNotNone(file_elements)
        self.assertEqual(len(file_elements), 0)

    def test_can_show_summary(self):
        pygount_folder = os.path.dirname(os.path.dirname(__file__))
        exit_code = command.pygount_command(['--summary', pygount_folder])
        self.assertEqual(exit_code, 0)
