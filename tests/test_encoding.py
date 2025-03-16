"""
Tests for encoding related functions.
"""

# Copyright (c) 2016-2025, Thomas Aglassinger.
# All rights reserved. Distributed under the BSD License.
from tempfile import NamedTemporaryFile

import pytest

from pygount.analysis import _BOM_TO_ENCODING_MAP, encoding_for, encoding_from_possible_magic_comment, is_binary_file

from ._common import temp_binary_file, temp_source_file

_ENCODING_TO_BOM_MAP = {encoding: bom for bom, encoding in _BOM_TO_ENCODING_MAP.items()}
_TEST_CODE = "x = '\u00fd \u20ac'"


@pytest.mark.parametrize(
    "ascii_header",
    [
        "# encoding: cp1252",
        "# coding: cp1252",
        "# -*- coding: cp1252 -*-",
        "# eNcOdInG: cp1252",
        "## encoding: cp1252",
        "#encoding:cp1252",
        "# -*- coding: cp1252; mode: python; -*-"  # Emacs modeline
        "/* coding: cp1252 */"  # C
        "{ coding: cp1252 }"  # Pascal
        "REM coding: cp1252",  # Basic
    ],
)
def test_can_detect_encoding_from_magic_comments(ascii_header: str):
    assert encoding_from_possible_magic_comment(ascii_header) == "cp1252"


@pytest.mark.parametrize(
    "ascii_header",
    [
        "",
        "    ",
        " # encoding: cp1252",  # Leading white space
        "# encoding: !$%&",
        "-*- coding: cp1252 -*-",  # Not a comment
        "encoding: cp1252",
        '{"x":"encoding: cp1252"}',
    ],
)
def test_can_ignore_encoding_from_magic_comments(ascii_header: str):
    assert encoding_from_possible_magic_comment(ascii_header) is None


@pytest.mark.parametrize("encoding", _BOM_TO_ENCODING_MAP.values())
def test_can_detect_bom_encodings(encoding: str):
    _test_can_detect_bom_encoding(encoding)


def _test_can_detect_bom_encoding(encoding: str):
    with NamedTemporaryFile(mode="wb+", suffix="txt") as test_file:
        if encoding != "utf-8-sig":
            bom = _ENCODING_TO_BOM_MAP[encoding]
            test_file.write(bom)
        test_file.write(_TEST_CODE.encode(encoding))
        test_file.flush()
        test_file.seek(0)
        actual_encoding = encoding_for(test_file.name)
    assert actual_encoding == encoding


@pytest.mark.parametrize("encoding", ["cp1252", "utf-8"])
def test_can_detect_plain_encoding(encoding: str):
    with temp_source_file("txt", _TEST_CODE, encoding=encoding) as test_file:
        actual_encoding = encoding_for(test_file.name)
        assert actual_encoding == encoding


def test_can_detect_xml_prolog():
    encoding = "iso-8859-15"
    xml_code = f'<?xml encoding="{encoding}" standalone="yes"?><some>{_TEST_CODE}</some>'
    with temp_source_file("xml", [xml_code], encoding=encoding) as test_file:
        actual_encoding = encoding_for(test_file.name)
    assert actual_encoding == encoding


def test_can_detect_magic_comment():
    encoding = "iso-8859-15"
    lines = ["#!/usr/bin/python", f"# -*- coding: {encoding} -*-", _TEST_CODE]
    with temp_source_file("txt", lines, encoding=encoding) as test_file:
        actual_encoding = encoding_for(test_file.name)
    assert actual_encoding == encoding


def test_can_detect_automatic_encoding_for_empty_source():
    with temp_binary_file(b"") as test_file:
        actual_encoding = encoding_for(test_file.name)
    assert actual_encoding == "utf-8"


def test_can_detect_chardet_encoding():
    test_path = __file__
    actual_encoding = encoding_for(test_path)
    assert actual_encoding == "utf-8"


def test_can_detect_utf8_when_cp1252_would_fail():
    # Write closing double quote in UTF-8, which contains 0x9d,
    # which fails when read as CP1252.
    content = b"\xe2\x80\x9d"
    with temp_binary_file(content) as test_file:
        actual_encoding = encoding_for(test_file.name, encoding="automatic", fallback_encoding=None)
        assert actual_encoding == "utf-8"
        actual_encoding = encoding_for(test_file.name, encoding="automatic", fallback_encoding="cp1252")
        assert actual_encoding == "cp1252"


def test_can_use_hardcoded_encoding():
    with temp_source_file("txt", "\N{EURO SIGN}", encoding="cp1252") as test_file:
        test_path = test_file.name
        actual_encoding = encoding_for(test_path, "utf-8")
        assert actual_encoding == "utf-8"
        # Make sure that we cannot actually read the file using the hardcoded but wrong encoding.
        with open(test_path, encoding=actual_encoding) as broken_test_file, pytest.raises(UnicodeDecodeError):
            broken_test_file.read()


def test_can_detect_binary_with_zero_byte():
    with temp_binary_file(b"hello\0world") as binary_file:
        assert is_binary_file(binary_file.name)


def test_can_detect_utf16_as_non_binary():
    with NamedTemporaryFile(encoding="utf-16", mode="w+") as utf16_file:
        utf16_file.write("Hello world!")
        utf16_file.flush()
        utf16_file.seek(0)
        assert not is_binary_file(utf16_file.name)
