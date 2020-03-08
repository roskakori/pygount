"""
Tests for pygount source code analysis.
"""
# Copyright (c) 2016-2020, Thomas Aglassinger.
# All rights reserved. Distributed under the BSD License.
import atexit
import glob
import os
import pytest
import shutil
import tempfile
import unittest

from pygments import lexers, token

from pygount import analysis
from pygount import common


_TESTS_FOLDER = os.path.dirname(__file__)
_TESTS_TEMP_FOLDER = os.path.join(_TESTS_FOLDER, ".temp")


def _test_path(name, suffix="tmp"):
    result = os.path.join(tempfile.gettempdir(), "pygount_tests_EncodingTest_" + name + "." + suffix)
    atexit.register(os.remove, result)
    return result


def _write_test_file(path, lines=list(), encoding="utf-8"):
    with open(path, "w", encoding=encoding) as test_file:
        for line in lines:
            test_file.write(line + "\n")


class SourceScannerTest(unittest.TestCase):
    def setUp(self):
        self._tests_folder = os.path.dirname(__file__)

    def test_can_find_no_files(self):
        scanner = analysis.SourceScanner([])
        actual_paths = list(scanner.source_paths())
        assert actual_paths == []

    def test_can_find_any_files(self):
        scanner = analysis.SourceScanner([self._tests_folder])
        actual_paths = list(scanner.source_paths())
        assert actual_paths != []

    def test_can_find_python_files(self):
        scanner = analysis.SourceScanner([self._tests_folder], "py")
        actual_paths = list(scanner.source_paths())
        assert actual_paths != []
        for python_path, _ in actual_paths:
            actual_suffix = os.path.splitext(python_path)[1]
            assert actual_suffix == ".py"

    def test_can_skip_folder(self):
        NAME_TO_SKIP = "source_to_skip.py"
        folder_to_skip = os.path.join(self._tests_folder, ".test_can_skip_folder")
        os.makedirs(folder_to_skip, exist_ok=True)
        try:
            _write_test_file(os.path.join(folder_to_skip, NAME_TO_SKIP), ["# Test", "print(1)"])
            scanner = analysis.SourceScanner([self._tests_folder], "py")
            for python_path, _ in scanner.source_paths():
                actual_name = os.path.basename(python_path)
                assert actual_name != NAME_TO_SKIP
        finally:
            shutil.rmtree(folder_to_skip)


class AnalysisTest(unittest.TestCase):
    def test_can_deline_tokens(self):
        assert list(analysis._delined_tokens([(token.Comment, "# a")])) == [(token.Comment, "# a")]
        assert list(analysis._delined_tokens([(token.Comment, "# a\n#  b")])) == [
            (token.Comment, "# a\n"),
            (token.Comment, "#  b"),
        ]
        assert list(analysis._delined_tokens([(token.Comment, "# a\n#  b\n")])) == [
            (token.Comment, "# a\n"),
            (token.Comment, "#  b\n"),
        ]
        assert list(analysis._delined_tokens([(token.Comment, "# a\n#  b\n # c\n")])) == [
            (token.Comment, "# a\n"),
            (token.Comment, "#  b\n"),
            (token.Comment, " # c\n"),
        ]

    def test_can_compute_python_line_parts(self):
        python_lexer = lexers.get_lexer_by_name("python")
        assert list(analysis._line_parts(python_lexer, "#")) == [set("d")]
        assert list(analysis._line_parts(python_lexer, "s = 'x'  # x")) == [set("cds")]

    def test_can_detect_white_text(self):
        python_lexer = lexers.get_lexer_by_name("python")
        assert list(analysis._line_parts(python_lexer, "{[()]};")) == [set()]
        assert list(analysis._line_parts(python_lexer, "pass")) == [set()]

    def test_can_convert_python_strings_to_comments(self):
        source_code = (
            "#!/bin/python\n" '"Some tool."\n' "#(C) by me\n" "def x():\n" '    "Some function"\n' "    return 1"
        )
        python_lexer = lexers.get_lexer_by_name("python")
        python_tokens = python_lexer.get_tokens(source_code)
        for token_type, token_text in list(analysis._pythonized_comments(analysis._delined_tokens(python_tokens))):
            assert token_type not in token.String

    def test_can_analyze_python(self):
        source_code = (
            '"Some tool."\n' "#!/bin/python\n" "#(C) by me\n" "def x():\n" '    "Some function"\n' '    return "abc"\n'
        )
        python_lexer = lexers.get_lexer_by_name("python")
        actual_line_parts = list(analysis._line_parts(python_lexer, source_code))
        expected_line_parts = [{"d"}, {"d"}, {"d"}, {"c"}, {"d"}, {"c", "s"}]
        assert actual_line_parts == expected_line_parts

    def test_can_analyze_encoding_error(self):
        test_path = _test_path("encoding_error", "py")
        with open(test_path, "w", encoding="cp1252") as test_file:
            test_file.write('print("\N{EURO SIGN}")')
        source_analysis = analysis.source_analysis(test_path, "test", encoding="utf-8")
        assert source_analysis.language == "__error__"
        assert source_analysis.state == analysis.SourceState.error.name
        assert "0x80" in str(source_analysis.state_info)

    def test_can_detect_silent_dos_batch_remarks(self):
        test_bat_path = _test_path("test_can_detect_silent_dos_batch_remarks", "bat")
        _write_test_file(test_bat_path, ["rem normal comment", "@rem silent comment", "echo some code"])
        source_analysis = analysis.source_analysis(test_bat_path, "test", encoding="utf-8")
        assert source_analysis.language == "Batchfile"
        assert source_analysis.code == 1
        assert source_analysis.documentation == 2

    def test_fails_on_unknown_magic_encoding_comment(self):
        test_path = _test_path("unknown_magic_encoding_comment", "py")
        with open(test_path, "w", encoding="utf-8") as test_file:
            test_file.write("# -*- coding: no_such_encoding -*-")
            test_file.write('print("hello")')
        no_such_encoding = analysis.encoding_for(test_path)
        assert no_such_encoding == "no_such_encoding"
        source_analysis = analysis.source_analysis(test_path, "test", encoding=no_such_encoding)
        assert source_analysis.language == "__error__"
        assert source_analysis.state == analysis.SourceState.error.name
        assert "unknown encoding" in str(source_analysis.state_info)

    def test_can_analyze_oracle_sql(self):
        test_oracle_sql_path = _test_path("test_can_analyze_oracle_sql", "pls")
        _write_test_file(
            test_oracle_sql_path, ["-- Oracle SQL example using an obscure suffix.", "select *", "from some_table;"]
        )
        source_analysis = analysis.source_analysis(test_oracle_sql_path, "test", encoding="utf-8")
        assert source_analysis.language.lower().endswith("sql")
        assert source_analysis.code == 2
        assert source_analysis.documentation == 1

    def test_can_analyze_webfocus(self):
        test_fex_path = _test_path("test_can_analyze_webfocus", "fex")
        _write_test_file(test_fex_path, ["-* comment", "-type some text", "table file some print * end;"])
        source_analysis = analysis.source_analysis(test_fex_path, "test", encoding="utf-8")
        assert source_analysis.language == "WebFOCUS"
        assert source_analysis.code == 2
        assert source_analysis.documentation == 1


class BinaryTest(unittest.TestCase):
    def test_can_detect_binary_source_code(self):
        binary_path = _test_path("some_django", "mo")
        with open(binary_path, "wb") as binary_file:
            binary_file.write(b"hello\0world!")
        source_analysis = analysis.source_analysis(binary_path, "test", encoding="utf-8")
        assert source_analysis.state == analysis.SourceState.binary.name
        assert source_analysis.code == 0


class EncodingTest(unittest.TestCase):
    _ENCODING_TO_BOM_MAP = dict((encoding, bom) for bom, encoding in analysis._BOM_TO_ENCODING_MAP.items())
    _TEST_CODE = "x = '\u00fd \u20ac'"

    def _test_can_detect_bom_encoding(self, encoding):
        test_path = _test_path(encoding)
        with open(test_path, "wb") as test_file:
            if encoding != "utf-8-sig":
                bom = EncodingTest._ENCODING_TO_BOM_MAP[encoding]
                test_file.write(bom)
            test_file.write(EncodingTest._TEST_CODE.encode(encoding))
        actual_encoding = analysis.encoding_for(test_path)
        assert actual_encoding == encoding

    def test_can_detect_bom_encodings(self):
        for _, encoding in analysis._BOM_TO_ENCODING_MAP.items():
            self._test_can_detect_bom_encoding(encoding)

    def test_can_detect_plain_encoding(self):
        for encoding in ("cp1252", "utf-8"):
            test_path = _test_path(encoding)
            with open(test_path, "w", encoding=encoding) as test_file:
                test_file.write(EncodingTest._TEST_CODE)
            actual_encoding = analysis.encoding_for(test_path)
            assert actual_encoding == encoding

    def test_can_detect_xml_prolog(self):
        encoding = "iso-8859-15"
        test_path = _test_path("xml-" + encoding)
        with open(test_path, "w", encoding=encoding) as test_file:
            xml_code = '<?xml encoding="{0}" standalone="yes"?><some>{1}</some>'.format(
                encoding, EncodingTest._TEST_CODE
            )
            test_file.write(xml_code)
        actual_encoding = analysis.encoding_for(test_path)
        assert actual_encoding == encoding

    def test_can_detect_magic_comment(self):
        encoding = "iso-8859-15"
        test_path = _test_path("magic-" + encoding)
        with open(test_path, "w", encoding=encoding) as test_file:
            test_file.write("#!/usr/bin/python\n")
            test_file.write("# -*- coding: {0} -*-\n".format(encoding))
            test_file.write(EncodingTest._TEST_CODE)
        actual_encoding = analysis.encoding_for(test_path)
        assert actual_encoding == encoding

    def test_can_detect_automatic_encoding_for_empty_source(self):
        test_path = _test_path("empty")
        with open(test_path, "wb") as _:
            pass  # Write empty file.
        actual_encoding = analysis.encoding_for(test_path)
        assert actual_encoding == "utf-8"

    def test_can_detect_chardet_encoding(self):
        test_path = __file__
        actual_encoding = analysis.encoding_for(test_path)
        assert actual_encoding == "utf-8"

    def test_can_detect_utf8_when_cp1252_would_fail(self):
        test_path = _test_path("utf-8_ok_cp1252_broken")
        with open(test_path, "wb") as test_file:
            # Write closing double quote in UTF-8, which contains 0x9d,
            # which fails when read as CP1252.
            test_file.write(b"\xe2\x80\x9d")
        actual_encoding = analysis.encoding_for(test_path, encoding="automatic", fallback_encoding=None)
        assert actual_encoding == "utf-8"
        actual_encoding = analysis.encoding_for(test_path, encoding="automatic", fallback_encoding="cp1252")
        assert actual_encoding == "cp1252"

    def test_can_use_hardcoded_ending(self):
        test_path = _test_path("hardcoded_cp1252")
        with open(test_path, "w", encoding="cp1252") as test_file:
            test_file.write("\N{EURO SIGN}")
        actual_encoding = analysis.encoding_for(test_path, "utf-8")
        assert actual_encoding == "utf-8"
        # Make sure that we cannot actually read the file using the hardcoded but wrong encoding.
        with open(test_path, "r", encoding=actual_encoding) as broken_test_file:
            with pytest.raises(UnicodeDecodeError):
                broken_test_file.read()

    def test_can_detect_binary_with_zero_byte(self):
        test_path = _test_path("binary")
        with open(test_path, "wb") as test_file:
            test_file.write(b"hello\0world")
        assert analysis.is_binary_file(test_path)

    def test_can_detect_utf16_as_non_binary(self):
        test_path = _test_path("utf-16")
        with open(test_path, "w", encoding="utf-16") as test_file:
            test_file.write("Hello world!")
        assert not analysis.is_binary_file(test_path)


class GeneratedCodeTest(unittest.TestCase):
    _STANDARD_SOURCE_LINES = """#!/bin/python3
    # Example code for
    # generated source code.
    print("I'm generated!")
    """.split(
        "\n"
    )
    _STANDARD_GENERATED_REGEXES = common.regexes_from(
        common.REGEX_PATTERN_PREFIX + ".*some,.*other,.*generated,.*print"
    )

    def test_can_detect_non_generated_code(self):
        _DEFAULT_GENERATED_REGEXES = common.regexes_from(analysis.DEFAULT_GENERATED_PATTERNS_TEXT)
        with open(__file__, "r", encoding="utf-8") as source_file:
            matching_line_number_and_regex = analysis.matching_number_line_and_regex(
                source_file, _DEFAULT_GENERATED_REGEXES
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
        generated_sql_path = _test_path("generated", "sql")
        with open(generated_sql_path, "w", encoding="utf-8") as generated_sql_file:
            generated_sql_file.write("-- Generiert mit Hau-Ruck-Franz-Deutsch.\n")
            generated_sql_file.write("select * from sauerkraut;\n")
        source_analysis = analysis.source_analysis(
            generated_sql_path, "test", generated_regexes=common.regexes_from("[regex](?i).*generiert")
        )
        assert source_analysis.state == analysis.SourceState.generated.name


class SizeTest(unittest.TestCase):
    def test_can_detect_empty_source_code(self):
        empty_py_path = _test_path("empty", "py")
        _write_test_file(empty_py_path)
        source_analysis = analysis.source_analysis(empty_py_path, "test", encoding="utf-8")
        assert source_analysis.state == analysis.SourceState.empty.name
        assert source_analysis.code == 0


class TextTest(unittest.TestCase):
    def test_can_analyze_project_text_files(self):
        project_root_folder = os.path.dirname(_TESTS_FOLDER)
        for text_path in glob.glob(os.path.join(project_root_folder, "*.txt")):
            source_analysis = analysis.source_analysis(text_path, "test")
            assert source_analysis.state == analysis.SourceState.analyzed.name
            assert source_analysis.documentation > 0
            if "requirements.txt" not in text_path:
                assert source_analysis.empty > 0


class DuplicatePoolTest(unittest.TestCase):
    def test_can_distinguish_different_files(self):
        some_path = _test_path(__name__ + "_some")
        _write_test_file(some_path, [])
        other_path = _test_path(__name__ + "_other")
        _write_test_file(other_path, ["x"])
        duplicate_pool = analysis.DuplicatePool()
        assert duplicate_pool.duplicate_path(some_path) is None
        assert duplicate_pool.duplicate_path(other_path) is None

    def test_can_detect_duplicate(self):
        original_path = _test_path(__name__ + "_original")
        _write_test_file(original_path, ["x"])
        duplicate_path = _test_path(__name__ + "_duplicate")
        _write_test_file(duplicate_path, ["x"])
        duplicate_pool = analysis.DuplicatePool()
        assert duplicate_pool.duplicate_path(original_path) is None
        assert original_path == duplicate_pool.duplicate_path(duplicate_path)

    def test_has_no_duplicate_in_pygount_source(self):
        project_folder = os.path.dirname(os.path.dirname(__file__))
        duplicate_pool = analysis.DuplicatePool()
        source_paths = []
        for sub_folder_name in ("pygount", "tests"):
            source_paths.extend(
                [
                    os.path.join(project_folder, sub_folder_name, source_name)
                    for source_name in os.listdir(os.path.join(project_folder, sub_folder_name))
                ]
            )
        for source_path in source_paths:
            if source_path.endswith(".py"):
                duplicate_path = duplicate_pool.duplicate_path(source_path)
                assert duplicate_path is None, "{0} must not be duplicate of {1}".format(source_path, duplicate_path)
