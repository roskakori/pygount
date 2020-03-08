"""
Tests for :py:mod:`pygount.common` module.
"""
# Copyright (c) 2016-2020, Thomas Aglassinger.
# All rights reserved. Distributed under the BSD License.
import re

import pygount.common


def test_can_build_str():
    error_without_source = pygount.common.OptionError("test")
    assert str(error_without_source) == "test"

    error_with_source = pygount.common.OptionError("test", "some_file.txt")
    assert str(error_with_source) == "some_file.txt: test"


def test_can_match_from_regex():
    regex = pygount.common.regex_from(re.compile(r"a\d+b"))
    assert regex.match("a123b") is not None
    assert regex.match("ab") is None


def test_can_match_from_regex_pattern():
    regex = pygount.common.regex_from(r"a\d+b")
    assert regex.match("a123b") is not None
    assert regex.match("ab") is None


def test_can_match_from_shell_pattern():
    regex = pygount.common.regex_from("*a[0-9]?*b*", True)
    assert regex.match("a123b") is not None
    assert regex.match("ab") is None


def test_can_match_single_regex_from_shell_pattern():
    regexes = pygount.common.regexes_from("*.py")
    assert len(regexes) == 1
    assert regexes[0].match("some.py") is not None
    assert regexes[0].match("some.bat") is None


def test_can_match_single_regex():
    regexes = pygount.common.regexes_from(pygount.common.REGEX_PATTERN_PREFIX + r"^.+\.py$")
    assert len(regexes) == 1
    assert regexes[0].match("some.py") is not None
    assert regexes[0].match("some.bat") is None


def test_can_match_regex_from_multiple_regex_patterns():
    regexes = pygount.common.regexes_from(pygount.common.REGEX_PATTERN_PREFIX + r"x, abc, ^.+\.py$")
    assert len(regexes) == 3
    assert regexes[0].match("some.py") is None
    assert regexes[1].match("some.py") is None
    assert regexes[2].match("some.py") is not None


def test_can_match_regex_from_multiple_default_shell_patterns():
    regexes = pygount.common.regexes_from(
        pygount.common.REGEX_PATTERN_PREFIX + pygount.common.ADDITIONAL_PATTERN + r"x", "abc, *.py"
    )
    assert len(regexes) == 3
    assert regexes[0].match("some.py") is None
    assert regexes[1].match("some.py") is None
    assert regexes[2].match("some.py") is not None
    assert regexes[0].match("x") is not None


def test_can_represent_text_as_list():
    assert pygount.common.as_list("") == []
    assert pygount.common.as_list("a") == ["a"]
    assert pygount.common.as_list("abc,d, e") == ["abc", "d", "e"]
    assert pygount.common.as_list(",,,,") == []


def test_can_represent_iterable_as_list():
    assert pygount.common.as_list([]) == []
    assert pygount.common.as_list(["a", 1, None]) == ["a", 1, None]
    assert pygount.common.as_list(tuple()) == []
    assert pygount.common.as_list(range(3)) == [0, 1, 2]


def test_can_convert_empty_text_to_lines():
    assert list(pygount.common.lines("")) == []


def test_can_convert_single_letter_to_lines():
    assert list(pygount.common.lines("a")) == ["a"]


def test_can_convert_single_letter_with_newline_to_lines():
    assert list(pygount.common.lines("a\n")) == ["a"]


def test_can_convert_multiple_lines():
    assert list(pygount.common.lines("a\nbc")) == ["a", "bc"]
    assert list(pygount.common.lines("a\nbc\n")) == ["a", "bc"]


def test_can_convert_empty_lines():
    assert list(pygount.common.lines("\n\n\n")) == ["", "", ""]
