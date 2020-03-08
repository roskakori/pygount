"""
Tests for pygount command line interface.
"""
# Copyright (c) 2016-2020, Thomas Aglassinger.
# All rights reserved. Distributed under the BSD License.
import os
import pytest
import tempfile
from xml.etree import ElementTree

from pygount import command
from pygount.command import Command, VALID_OUTPUT_FORMATS
from pygount.common import OptionError
from tests._common import PYGOUNT_PROJECT_FOLDER, PYGOUNT_SOURCE_FOLDER, TempFolderTest


class CommandTest(TempFolderTest):
    def test_fails_on_unknown_output_format(self):
        unknown_output_format = "no_such_output_format"
        command = Command()
        with pytest.raises(OptionError, match=unknown_output_format):
            command.set_output_format(unknown_output_format)

    def test_can_set_encoding(self):
        command = Command()
        command.set_encodings("automatic;cp1252")
        assert command.default_encoding == "automatic"
        assert command.fallback_encoding == "cp1252"

    def test_can_execute_on_own_code(self):
        output_path = os.path.join(self.tests_temp_folder, "test_can_execute_on_own_code.txt")
        try:
            os.remove(output_path)
        except FileNotFoundError:  # pragma: no cover
            pass  # Ignore missing file as it is going to be recreated.
        command = Command()
        command.set_output(output_path)
        command.set_output_format("cloc-xml")
        command.set_source_patterns(PYGOUNT_SOURCE_FOLDER)
        command.set_suffixes("py")
        command.execute()
        cloc_xml_root = ElementTree.parse(output_path)
        file_elements = cloc_xml_root.findall("files/file")
        assert file_elements is not None
        assert len(file_elements) >= 1

    def test_fails_on_broken_regex(self):
        command = Command()
        with pytest.raises(OptionError, match=r"^option --generated: cannot parse pattern for regular repression.*"):
            command.set_generated_regexps("[regex](", "option --generated")

    def test_can_use_chardet_for_encoding(self):
        command = Command()
        command.set_encodings("chardet")
        command.set_source_patterns(PYGOUNT_SOURCE_FOLDER)
        command.execute()


class PygountCommandTest(TempFolderTest):
    def test_can_show_help(self):
        with pytest.raises(SystemExit) as error_info:
            command.pygount_command(["--help"])
        assert error_info.value.code == 0

    def test_can_show_version(self):
        with pytest.raises(SystemExit) as error_info:
            command.pygount_command(["--version"])
        assert error_info.value.code == 0

    def test_fails_on_unknown_encoding(self):
        with pytest.raises(SystemExit) as error_info:
            command.pygount_command(["--encoding", "no_such_encoding", tempfile.gettempdir()])
        assert error_info.value.code == 2

    def test_fails_on_unknown_format(self):
        with pytest.raises(SystemExit) as error_info:
            command.pygount_command(["--format", "no_such_encoding", tempfile.gettempdir()])
        assert error_info.value.code == 2

    def test_fails_on_broken_regex_pattern(self):
        exit_code = command.pygount_command(["--generated", "[regex](", tempfile.gettempdir()])
        assert exit_code == 1

    def test_can_analyze_pygount_setup_py(self):
        pygount_setup_py_path = os.path.join(PYGOUNT_PROJECT_FOLDER, "setup.py")
        exit_code = command.pygount_command(["--verbose", pygount_setup_py_path])
        assert exit_code == 0

    def test_can_analyze_pygount_source_code(self):
        exit_code = command.pygount_command(["--verbose", PYGOUNT_SOURCE_FOLDER])
        assert exit_code == 0

    def test_can_detect_generated_code(self):
        generated_code_path = os.path.join(self.tests_temp_folder, "generated.py")
        with open(generated_code_path, "w", encoding="utf-8") as generated_code_file:
            generated_code_file.write(
                "# Generated with pygount.test_command.PygountCommandTest.test_can_detect_generated_code.\n"
            )
            generated_code_file.write("# Do not edit!\n")
            generated_code_file.write("print('hello World')\n")
        cloc_xml_path = os.path.join(self.tests_temp_folder, "cloc.xml")
        exit_code = command.pygount_command(
            ["--verbose", "--format", "cloc-xml", "--out", cloc_xml_path, generated_code_path]
        )
        assert exit_code == 0
        assert os.path.exists(cloc_xml_path)
        cloc_xml_root = ElementTree.parse(cloc_xml_path)
        file_elements = cloc_xml_root.findall("files/file[@language='__generated__']")
        assert file_elements is not None
        assert len(file_elements) >= 1

    def test_can_detect_generated_code_with_own_pattern(self):
        generiert_py_path = os.path.join(self.tests_temp_folder, "generiert.py")
        with open(generiert_py_path, "w", encoding="utf-8") as generiert_py_file:
            generiert_py_file.write(
                "# Generiert mit pygount.test_command.PygountCommandTest."
                "test_can_detect_generated_code_with_own_pattern()\n"
            )
            generiert_py_file.write("print('hello World')\n")
        cloc_xml_path = os.path.join(self.tests_temp_folder, "cloc.xml")
        exit_code = command.pygount_command(
            [
                "--verbose",
                "--format=cloc-xml",
                "--generated=[regex](?i).*generiert",
                "--out",
                cloc_xml_path,
                generiert_py_path,
            ]
        )
        assert exit_code == 0
        assert os.path.exists(cloc_xml_path)
        cloc_xml_root = ElementTree.parse(cloc_xml_path)
        file_elements = cloc_xml_root.findall("files/file[@language='__generated__']")
        assert file_elements is not None
        assert len(file_elements) >= 1

    def test_can_analyze_pygount_source_code_as_cloc_xml(self):
        cloc_xml_path = os.path.join(self.tests_temp_folder, "cloc.xml")
        exit_code = command.pygount_command(
            ["--verbose", "--format", "cloc-xml", "--out", cloc_xml_path, PYGOUNT_SOURCE_FOLDER]
        )
        assert exit_code == 0
        assert os.path.exists(cloc_xml_path)
        cloc_xml_root = ElementTree.parse(cloc_xml_path)
        file_elements = cloc_xml_root.findall("files/file")
        assert file_elements is not None
        assert len(file_elements) >= 1

    def test_can_detect_duplicates(self):
        source_code = "# Duplicate source\nprint('duplicate code')\n"
        original_path = os.path.join(self.tests_temp_folder, "original.py")
        with open(original_path, "w") as original_file:
            original_file.write(source_code)
        duplicate_path = os.path.join(self.tests_temp_folder, "duplicate.py")
        with open(duplicate_path, "w") as duplicate_file:
            duplicate_file.write(source_code)
        cloc_xml_path = os.path.join(self.tests_temp_folder, "cloc.xml")
        exit_code = command.pygount_command(
            ["--verbose", "--format", "cloc-xml", "--out", cloc_xml_path, original_path, duplicate_path]
        )
        assert exit_code == 0
        assert os.path.exists(cloc_xml_path)
        cloc_xml_root = ElementTree.parse(cloc_xml_path)
        file_elements = cloc_xml_root.findall("files/file[@language='__duplicate__']")
        assert file_elements is not None
        assert len(file_elements) == 1

    def test_can_accept_duplicates(self):
        source_code = "# Duplicate source\nprint('duplicate code')\n"
        original_path = os.path.join(self.tests_temp_folder, "original.py")
        with open(original_path, "w") as original_file:
            original_file.write(source_code)
        duplicate_path = os.path.join(self.tests_temp_folder, "duplicate.py")
        with open(duplicate_path, "w") as duplicate_file:
            duplicate_file.write(source_code)
        cloc_xml_path = os.path.join(self.tests_temp_folder, "cloc.xml")
        exit_code = command.pygount_command(
            ["--duplicates", "--verbose", "--format", "cloc-xml", "--out", cloc_xml_path, original_path, duplicate_path]
        )
        assert exit_code == 0
        assert os.path.exists(cloc_xml_path)
        cloc_xml_root = ElementTree.parse(cloc_xml_path)
        file_elements = cloc_xml_root.findall("files/file[@language='__duplicate__']")
        assert file_elements is not None
        assert len(file_elements) == 0

    def test_can_write_all_output_formats(self):
        for output_format in VALID_OUTPUT_FORMATS:
            exit_code = command.pygount_command(["--format", output_format, PYGOUNT_SOURCE_FOLDER])
            self.assertEqual(exit_code, 0)
