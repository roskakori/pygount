"""
Tests for pygount source code analysis.
"""

# Copyright (c) 2016-2024, Thomas Aglassinger.
# All rights reserved. Distributed under the BSD License.
import glob
import os
import unittest
from io import BytesIO, StringIO

import pytest
from pygments import lexers, token

import pygount
from pygount import Error as PygountError
from pygount import analysis, common
from pygount.analysis import (
    _delined_tokens,
    _line_parts,
    _pythonized_comments,
    base_language,
    guess_lexer,
    is_markup_file,
)

from ._common import PYGOUNT_PROJECT_FOLDER, PYGOUNT_SOURCE_FOLDER, TempFolderTest, temp_source_file
from .test_xmldialect import EXAMPLE_ANT_CODE


class SourceScannerTest(TempFolderTest):
    def setUp(self):
        super().setUp()
        self._tests_folder = os.path.dirname(__file__)

    def test_can_find_no_files(self):
        scanner = analysis.SourceScanner([])
        actual_paths = list(scanner.source_paths())
        assert actual_paths == []

    def test_can_find_any_files(self):
        scanner = analysis.SourceScanner([PYGOUNT_SOURCE_FOLDER])
        actual_paths = list(scanner.source_paths())
        assert actual_paths != []

    def test_can_find_python_files(self):
        scanner = analysis.SourceScanner([PYGOUNT_SOURCE_FOLDER], "py")
        actual_paths = list(scanner.source_paths())
        assert actual_paths != []
        for path_data in actual_paths:
            actual_suffix = os.path.splitext(path_data.source_path)[1]
            assert actual_suffix == ".py"

    def test_can_skip_dot_folder(self):
        project_folder_name = "project"
        project_folder = os.path.join(self.tests_temp_folder, project_folder_name)
        name_to_include = "include.py"
        relative_path_to_include = os.path.join(project_folder_name, "include", name_to_include)
        self.create_temp_file(relative_path_to_include, "include = 1", do_create_folder=True)
        relative_path_to_skip = os.path.join(project_folder_name, ".skip", "skip.py")
        self.create_temp_file(relative_path_to_skip, "skip = 2", do_create_folder=True)

        scanner = analysis.SourceScanner([project_folder])
        scanned_names = [os.path.basename(path_data.source_path) for path_data in scanner.source_paths()]
        assert scanned_names == [name_to_include]

    def test_succeeds_on_not_git_extension(self):
        non_repo_urls = [["https://github.com/roskakori/pygount/"], ["git@github.com:roskakori/pygount"]]
        for non_repo_url in non_repo_urls:
            with analysis.SourceScanner(non_repo_url) as scanner:
                _ = list(scanner.source_paths())

    def test_fails_on_non_git_urls(self):
        non_repo_urls = [["https://no/git/url"], ["https://google.com/nogit"]]
        for non_repo_url in non_repo_urls:
            with (
                analysis.SourceScanner(non_repo_url) as scanner,
                pytest.raises(pygount.Error, match="URL to git repository"),
            ):
                _ = list(scanner.source_paths())

    def test_can_find_python_files_in_dot(self):
        scanner = analysis.SourceScanner(["."], "py")
        actual_paths = list(scanner.source_paths())
        assert actual_paths != []
        for path_data in actual_paths:
            actual_suffix = os.path.splitext(path_data.source_path)[1]
            assert actual_suffix == ".py"

    def test_can_find_files_from_mixed_cloned_git_remote_url_and_local(self):
        git_remote_url = "https://github.com/roskakori/pygount.git"
        with analysis.SourceScanner([git_remote_url, PYGOUNT_SOURCE_FOLDER]) as scanner:
            actual_paths = list(scanner.source_paths())
            assert actual_paths != []
            assert actual_paths[0].source_path != actual_paths[-1].source_path
            assert actual_paths[-1].tmp_dir is not None


class AnalysisTest(unittest.TestCase):
    def test_can_deline_tokens(self):
        assert list(_delined_tokens([(token.Comment, "# a")])) == [(token.Comment, "# a")]
        assert list(_delined_tokens([(token.Comment, "# a\n#  b")])) == [
            (token.Comment, "# a\n"),
            (token.Comment, "#  b"),
        ]
        assert list(_delined_tokens([(token.Comment, "# a\n#  b\n")])) == [
            (token.Comment, "# a\n"),
            (token.Comment, "#  b\n"),
        ]
        assert list(_delined_tokens([(token.Comment, "# a\n#  b\n # c\n")])) == [
            (token.Comment, "# a\n"),
            (token.Comment, "#  b\n"),
            (token.Comment, " # c\n"),
        ]

    def test_can_compute_python_line_parts(self):
        python_lexer = lexers.get_lexer_by_name("python")
        assert list(_line_parts(python_lexer, "#")) == [set("d")]
        assert list(_line_parts(python_lexer, "s = 'x'  # x")) == [set("cds")]

    def test_can_detect_white_text(self):
        python_lexer = lexers.get_lexer_by_name("python")
        assert list(_line_parts(python_lexer, "{[()]};")) == [set()]
        assert list(_line_parts(python_lexer, "pass")) == [set()]

    def test_can_convert_python_strings_to_comments(self):
        source_code = '#!/bin/python\n"Some tool."\n#(C) by me\ndef x():\n    "Some function"\n    return 1'
        python_lexer = lexers.get_lexer_by_name("python")
        python_tokens = python_lexer.get_tokens(source_code)
        for token_type, _ in list(_pythonized_comments(_delined_tokens(python_tokens))):
            assert token_type not in token.String

    def test_can_analyze_python(self):
        source_lines = [
            '"Some tool."',
            "#!/bin/python",
            "#(C) by me",
            "def x():",
            '    "Some function"',
            '    return "abc"',
        ]
        actual_line_parts = _line_parts_with_detected_markup("python", source_lines)
        expected_line_parts = [{"d"}, {"d"}, {"d"}, {"c"}, {"d"}, {"c", "s"}]
        assert actual_line_parts == expected_line_parts

    def test_can_analyze_c(self):
        source_lines = [
            "/*",
            " * The classic hello world for C99.",
            " */",
            "#include <stdio.h>",
            "int main(void) {",
            '   puts("Hello, World!");',
            "}",
        ]
        actual_line_parts = _line_parts_with_detected_markup("c", source_lines)
        expected_line_parts = [{"d"}, {"d"}, {"d"}, {"c"}, {"c"}, {"c", "s"}, set()]
        assert actual_line_parts == expected_line_parts


def test_can_detect_all_lines_as_documentation_with_markup_enabled():
    source_lines = [
        "/*",
        " * The classic hello world for C99.",
        " */",
        "#include <stdio.h>",
        "int main(void) {",
        '   puts("Hello, World!");',
        "}",
    ]
    actual_line_parts = _line_parts_with_detected_markup("markdown", source_lines)
    assert all(line_part == "d" for line_part in actual_line_parts[-1])
    assert actual_line_parts[-1:] == [set()]


def _line_parts_with_detected_markup(lexer_name: str, source_lines: list[str]) -> list[set[str]]:
    lexer = lexers.get_lexer_by_name(lexer_name)
    is_markup = lexer_name in ["markdown", "md", "restructuredtext", "rst", "rest", "groff"]
    source_code = "\n".join(source_lines)
    return list(_line_parts(lexer, source_code, is_markup=is_markup))


class _NonSeekableEmptyBytesIO(BytesIO):
    # Class to create a 'dummy object that mimics a non-seekable file handle'
    def seekable(self) -> bool:
        return False


class FileAnalysisTest(TempFolderTest):
    def test_can_analyze_encoding_error(self):
        test_path = self.create_temp_file("encoding_error.py", 'print("\N{EURO SIGN}")', encoding="cp1252")
        source_analysis = analysis.SourceAnalysis.from_file(test_path, "test", encoding="utf-8")
        assert source_analysis.language == "__error__"
        assert source_analysis.state == analysis.SourceState.error
        assert "0x80" in str(source_analysis.state_info)

    def test_can_detect_silent_dos_batch_remarks(self):
        test_bat_path = self.create_temp_file(
            "test_can_detect_silent_dos_batch_remarks.bat",
            ["rem normal comment", "@rem silent comment", "echo some code"],
        )
        source_analysis = analysis.SourceAnalysis.from_file(test_bat_path, "test", encoding="utf-8")
        assert source_analysis.language == "Batchfile"
        assert source_analysis.code_count == 1
        assert source_analysis.documentation_count == 2

    def test_can_ignore_almost_magic_comment(self):
        test_bat_path = self.create_temp_file(
            "test_can_ignore_almost_magic_comment.json",
            ['{"x":"coding:no_such_coding"'],
        )
        source_analysis = analysis.SourceAnalysis.from_file(test_bat_path, "test")
        assert source_analysis.language.lower() == "json"
        assert source_analysis.code_count == 1
        assert source_analysis.documentation_count == 0

    def test_fails_on_unknown_magic_encoding_comment(self):
        test_path = self.create_temp_file(
            "test_fails_on_unknown_magic_encoding_comment.py", ["# -*- coding: no_such_encoding -*-", 'print("hello")']
        )
        no_such_encoding = analysis.encoding_for(test_path)
        assert no_such_encoding == "no_such_encoding"
        source_analysis = analysis.SourceAnalysis.from_file(test_path, "test", encoding=no_such_encoding)
        assert source_analysis.language == "__error__"
        assert source_analysis.state == analysis.SourceState.error
        assert "unknown encoding" in str(source_analysis.state_info)

    def test_can_analyze_oracle_sql(self):
        test_oracle_sql_path = self.create_temp_file(
            "test_can_analyze_oracle_sql.pls",
            ["-- Oracle SQL example using an obscure suffix.", "select *", "from some_table;"],
        )
        source_analysis = analysis.SourceAnalysis.from_file(test_oracle_sql_path, "test", encoding="utf-8")
        assert source_analysis.language.lower().endswith("sql")
        assert source_analysis.code_count == 2
        assert source_analysis.documentation_count == 1

    def test_can_analyze_webfocus(self):
        test_fex_path = self.create_temp_file(
            "some.fex", ["-* comment", "-type some text", "table file some print * end;"]
        )
        source_analysis = analysis.SourceAnalysis.from_file(test_fex_path, "test", encoding="utf-8")
        assert source_analysis.language == "WebFOCUS"
        assert source_analysis.code_count == 2
        assert source_analysis.documentation_count == 1

    def test_can_analyze_xml_dialect(self):
        build_xml_path = self.create_temp_file("build.xml", EXAMPLE_ANT_CODE)
        source_analysis = analysis.SourceAnalysis.from_file(build_xml_path, "test")
        assert source_analysis.state == analysis.SourceState.analyzed
        assert source_analysis.language == "Ant"

    def test_can_analyze_unknown_language(self):
        unknown_language_path = self.create_temp_file("some.unknown_language", ["some", "lines", "of", "text"])
        source_analysis = analysis.SourceAnalysis.from_file(unknown_language_path, "test")
        assert source_analysis.state == analysis.SourceState.unknown

    def test_can_detect_binary_source_code(self):
        binary_path = self.create_temp_binary_file("some_django.mo", b"hello\0world!")
        source_analysis = analysis.SourceAnalysis.from_file(binary_path, "test", encoding="utf-8")
        assert source_analysis.state == analysis.SourceState.binary
        assert source_analysis.code_count == 0

    def test_can_analyze_stringio(self):
        test_path = "imaginary/path/to/file.py"
        test_code = "from random import randint\n\n# Print a random dice roll\nprint(randint(6))\n"
        source_analysis = analysis.SourceAnalysis.from_file(test_path, "test", file_handle=StringIO(test_code))
        assert source_analysis.state == analysis.SourceState.analyzed
        assert source_analysis.language == "Python"
        assert source_analysis.code_count == 2

    def test_can_analyze_bytesio(self):
        test_path = "imaginary/path/to/file.py"
        test_code = b"from random import randint\n\n# Print a random dice roll\nprint(randint(6))\n"
        source_analysis = analysis.SourceAnalysis.from_file(test_path, "test", file_handle=BytesIO(test_code))
        assert source_analysis.state == analysis.SourceState.analyzed
        assert source_analysis.language == "Python"
        assert source_analysis.code_count == 2

    def test_can_analyze_embedded_language(self):
        test_html_django_path = self.create_temp_file(
            "some.html",
            ["<!DOCTYPE html>", "{% load i18n %}", '<html lang="{{ language_code }}" />'],
        )
        source_analysis = analysis.SourceAnalysis.from_file(test_html_django_path, "test", encoding="utf-8")
        assert source_analysis.language.lower() == "html+django/jinja"
        assert source_analysis.code_count == 3

    def test_can_merge_embedded_language(self):
        test_html_django_path = self.create_temp_file(
            "some.html",
            ["<!DOCTYPE html>", "{% load i18n %}", '<html lang="{{ language_code }}" />'],
        )
        source_analysis = analysis.SourceAnalysis.from_file(
            test_html_django_path, "test", encoding="utf-8", merge_embedded_language=True
        )
        assert source_analysis.language.lower() == "html"
        assert source_analysis.code_count == 3

    def test_can_analyze_unknown_magic_comment_encoding(self):
        test_python_path = self.create_temp_file("some.py", ["# -*- coding: no_such_encoding -*-", "print('hello')"])
        source_analysis = analysis.SourceAnalysis.from_file(test_python_path, "test")
        assert source_analysis.language.lower() == "__error__"
        assert source_analysis.state_info == "unknown encoding: no_such_encoding"

    def test_fails_on_non_seekable_file_handle_with_encoding_automatic(self):
        file_handle = _NonSeekableEmptyBytesIO()

        with pytest.raises(PygountError, match=r".*file handle must be seekable.*"):
            analysis.SourceAnalysis.from_file("README.md", "test", file_handle=file_handle, encoding="automatic")

    def test_fails_on_non_seekable_file_handle_with_encoding_chardet(self):
        file_handle = _NonSeekableEmptyBytesIO()

        with pytest.raises(PygountError, match=r".*file handle must be seekable.*"):
            analysis.SourceAnalysis.from_file("README.md", "test", file_handle=file_handle, encoding="chardet")


@pytest.mark.parametrize(
    "suffix, code_count, doc_count, expected_language_lower",
    [
        ("rst", 0, 3, "restructuredtext"),
        ("md", 0, 3, "markdown"),
        ("txt", 0, 3, "text only"),
        ("4", 0, 3, "groff"),
    ],
)
def test_can_analyze_markup_as_plain_documentation(
    suffix, code_count: int, doc_count: int, expected_language_lower: str
):
    source_lines = ["<!DOCTYPE html>", "{% load i18n %}", "", "  ", '<html lang="{{ language_code }}" />']
    expected_empty_count = 2
    expected_documentation_count = len(source_lines) - expected_empty_count
    with temp_source_file(suffix, source_lines) as test_file:
        source_analysis = analysis.SourceAnalysis.from_file(test_file.name, "test", encoding="utf-8")
        assert source_analysis.language.lower() == expected_language_lower
        assert source_analysis.code_count == 0
        assert source_analysis.documentation_count == expected_documentation_count
        assert source_analysis.empty_count == expected_empty_count


def test_can_repr_source_analysis_from_file():
    source_analysis = analysis.SourceAnalysis("some.py", "Python", "some", 1, 2, 3, 4, analysis.SourceState.analyzed)
    expected_source_analysis_repr = (
        "SourceAnalysis(path='some.py', language='Python', group='some', "
        "state=analyzed, code_count=1, documentation_count=2, empty_count=3, string_count=4)"
    )
    assert repr(source_analysis) == expected_source_analysis_repr
    assert repr(source_analysis) == str(source_analysis)


def test_can_repr_empty_source_analysis_from_file():
    source_analysis = analysis.SourceAnalysis("some.py", "__empty__", "some", 0, 0, 0, 0, analysis.SourceState.empty)
    expected_source_analysis_repr = "SourceAnalysis(path='some.py', language='__empty__', group='some', state=empty)"
    assert repr(source_analysis) == expected_source_analysis_repr
    assert repr(source_analysis) == str(source_analysis)


def test_can_repr_error_source_analysis_from_file():
    source_analysis = analysis.SourceAnalysis(
        "some.py", "__error__", "some", 0, 0, 0, 0, analysis.SourceState.error, "error details"
    )
    expected_source_analysis_repr = (
        "SourceAnalysis(path='some.py', language='__error__', group='some', state=error, state_info='error details')"
    )
    assert repr(source_analysis) == expected_source_analysis_repr
    assert repr(source_analysis) == str(source_analysis)


def test_can_guess_lexer_for_python():
    lexer = guess_lexer("some.py", "pass")
    assert lexer is not None
    assert lexer.name == "Python"


def test_can_guess_lexer_for_plain_text():
    lexer = guess_lexer("README.1st", "hello!")
    assert lexer is not None
    assert lexer.name == "Text"


def test_can_guess_lexer_for_cmakelists():
    source_code = "\n".join(
        [
            "cmake_minimum_required(VERSION 2.6)",
            "project(example)",
            "set(CMAKE_CXX_STANDARD 14)",
            "set(SOURCE_FILES example.cpp)",
            "add_executable(example ${SOURCE_FILES})",
        ]
    )
    lexer = guess_lexer("CMakeLists.txt", source_code)
    assert lexer is not None
    assert lexer.name == "CMake"


class GeneratedCodeTest(TempFolderTest):
    _STANDARD_SOURCE_LINES = [
        "#!/bin/python3",
        "    # Example code for",
        "    # generated source code.",
        '    print("I\'m generated!")',
        "    ",
    ]
    _STANDARD_GENERATED_REGEXES = common.regexes_from(
        common.REGEX_PATTERN_PREFIX + ".*some,.*other,.*generated,.*print"
    )

    def test_can_detect_non_generated_code(self):
        default_generated_regexes = common.regexes_from(analysis.DEFAULT_GENERATED_PATTERNS_TEXT)
        with open(__file__, encoding="utf-8") as source_file:
            matching_line_number_and_regex = analysis.matching_number_line_and_regex(
                source_file, default_generated_regexes
            )
        assert matching_line_number_and_regex is None

    def test_can_detect_generated_code(self):
        matching_number_line_and_regex = analysis.matching_number_line_and_regex(
            GeneratedCodeTest._STANDARD_SOURCE_LINES, GeneratedCodeTest._STANDARD_GENERATED_REGEXES
        )
        assert matching_number_line_and_regex is not None
        matching_number, matching_line, matching_regex = matching_number_line_and_regex
        assert matching_number == 2
        assert matching_line == GeneratedCodeTest._STANDARD_SOURCE_LINES[2]
        assert matching_regex == GeneratedCodeTest._STANDARD_GENERATED_REGEXES[2]

    def test_can_not_detect_generated_code_with_late_comment(self):
        non_matching_number_line_and_regex = analysis.matching_number_line_and_regex(
            GeneratedCodeTest._STANDARD_SOURCE_LINES, GeneratedCodeTest._STANDARD_GENERATED_REGEXES, 2
        )
        assert non_matching_number_line_and_regex is None

    def test_can_analyze_generated_code_with_own_pattern(self):
        lines = ["-- Generiert mit Hau-Ruck-Franz-Deutsch.", "select * from sauerkraut;"]
        generated_sql_path = self.create_temp_file("generated.sql", lines)
        source_analysis = analysis.SourceAnalysis.from_file(
            generated_sql_path, "test", generated_regexes=common.regexes_from("[regex](?i).*generiert")
        )
        assert source_analysis.state == analysis.SourceState.generated


class SizeTest(TempFolderTest):
    def test_can_detect_empty_source_code(self):
        empty_py_path = self.create_temp_binary_file("empty.py", b"")
        source_analysis = analysis.SourceAnalysis.from_file(empty_py_path, "test", encoding="utf-8")
        assert source_analysis.state == analysis.SourceState.empty
        assert source_analysis.code_count == 0


def test_can_analyze_project_markdown_files():
    project_root_folder = os.path.dirname(PYGOUNT_PROJECT_FOLDER)
    for text_path in glob.glob(os.path.join(project_root_folder, "*.md")):
        source_analysis = analysis.SourceAnalysis.from_file(text_path, "test")
        assert source_analysis.state == analysis.SourceState.analyzed
        assert source_analysis.documentation_count > 0
        assert source_analysis.empty_count > 0


def test_has_no_duplicate_in_pygount_source():
    duplicate_pool = analysis.DuplicatePool()
    source_paths = []
    for sub_folder_name in ("pygount", "tests"):
        source_paths.extend(
            [
                os.path.join(PYGOUNT_PROJECT_FOLDER, sub_folder_name, source_name)
                for source_name in os.listdir(os.path.join(PYGOUNT_PROJECT_FOLDER, sub_folder_name))
            ]
        )
    for source_path in source_paths:
        if source_path.endswith(".py"):
            duplicate_path = duplicate_pool.duplicate_path(source_path)
            assert duplicate_path is None, f"{source_path} must not be duplicate of {duplicate_path}"


def test_can_compute_base_language():
    assert base_language("JavaScript") == "JavaScript"
    assert base_language("JavaScript+Lasso") == "JavaScript"
    assert base_language("JavaScript+") == "JavaScript+"  # no actual language
    assert base_language("C++") == "C++"
    assert base_language("++C") == "++C"  # no actual language
    assert base_language("") == ""  # no actual language, but should not crash either


class DuplicatePoolTest(TempFolderTest):
    def test_can_distinguish_different_files(self):
        some_path = self.create_temp_file(__name__ + "_some", "some")
        other_path = self.create_temp_file(__name__ + "_other", "other")
        duplicate_pool = analysis.DuplicatePool()
        assert duplicate_pool.duplicate_path(some_path) is None
        assert duplicate_pool.duplicate_path(other_path) is None

    def test_can_detect_duplicate(self):
        same_content = "same"
        original_path = self.create_temp_file("original", same_content)
        duplicate_path = self.create_temp_file("duplicate", same_content)
        duplicate_pool = analysis.DuplicatePool()
        assert duplicate_pool.duplicate_path(original_path) is None
        assert original_path == duplicate_pool.duplicate_path(duplicate_path)


@pytest.mark.parametrize(
    "suffix, expected_result",
    [("md", True), ("MD", True), ("mD", True), ("rst", True), ("py", False), ("4", True), ("c", False)],
)
def test_can_detect_markup_file(suffix, expected_result):
    source_path = f"some_file_name.{suffix}"
    assert is_markup_file(source_path) == expected_result
