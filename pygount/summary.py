"""
Summaries of analyses of multiple source codes.
"""
# Copyright (c) 2016-2022, Thomas Aglassinger.
# All rights reserved. Distributed under the BSD License.
import functools
import re
from typing import Dict, Hashable

from .analysis import SourceAnalysis

_PSEUDO_LANGUAGE_REGEX = re.compile("^__[a-z]+__$")


@functools.total_ordering
class LanguageSummary:
    """
    Summary of a source code counts from multiple files of the same language.
    """

    def __init__(self, language: str):
        self._language = language
        self._code_count = 0
        self._documentation_count = 0
        self._empty_count = 0
        self._file_count = 0
        self._string_count = 0
        self._is_pseudo_language = _PSEUDO_LANGUAGE_REGEX.match(self.language) is not None

    @property
    def language(self) -> str:
        """the language to be summarized"""
        return self._language

    @property
    def code_count(self) -> int:
        """sum lines of code for this language"""
        return self._code_count

    @property
    def documentation_count(self) -> int:
        """sum lines of documentation for this language"""
        return self._documentation_count

    @property
    def empty_count(self) -> int:
        """sum empty lines for this language"""
        return self._empty_count

    @property
    def file_count(self) -> int:
        """number of source code files for this language"""
        return self._file_count

    @property
    def string_count(self) -> int:
        """sum number of lines containing only strings for this language"""
        return self._string_count

    @property
    def source_count(self) -> int:
        """sum number of source lines of code"""
        return self.code_count + self.string_count

    @property
    def is_pseudo_language(self) -> bool:
        """``True`` if the language is not a real programming language"""
        return self._is_pseudo_language

    def sort_key(self) -> Hashable:
        """sort key to sort multiple languages by importance"""
        return self.code_count, self.documentation_count, self.string_count, self.empty_count, self.language

    def __eq__(self, other):
        return self.sort_key() == other.sort_key()

    def __lt__(self, other):
        return self.sort_key() < other.sort_key()

    def add(self, source_analysis: SourceAnalysis) -> None:
        """
        Add counts from ``source_analysis`` to total counts for this language.
        """
        assert source_analysis is not None
        assert source_analysis.language == self.language

        self._file_count += 1
        if source_analysis.is_countable:
            self._code_count += source_analysis.code_count
            self._documentation_count += source_analysis.documentation_count
            self._empty_count += source_analysis.empty_count
            self._string_count += source_analysis.string_count

    def __repr__(self):
        result = "{0}(language={1!r}, file_count={2}".format(self.__class__.__name__, self.language, self.file_count)
        if not self.is_pseudo_language:
            result += ", code_count={0}, documentation_count={1}, empty_count={2}, string_count={3}".format(
                self.code_count, self.documentation_count, self.empty_count, self.string_count
            )
        result += ")"
        return result


class ProjectSummary:
    """
    Summary of source code counts for several languages and files.
    """

    def __init__(self):
        self._language_to_language_summary_map = {}
        self._total_code_count = 0
        self._total_documentation_count = 0
        self._total_empty_count = 0
        self._total_string_count = 0
        self._total_file_count = 0
        self._total_line_count = 0

    @property
    def language_to_language_summary_map(self) -> Dict[str, LanguageSummary]:
        """
        A map containing summarized counts for each language added with :py:meth:`add()` so far.
        """
        return self._language_to_language_summary_map

    @property
    def total_code_count(self) -> int:
        return self._total_code_count

    @property
    def total_documentation_count(self) -> int:
        return self._total_documentation_count

    @property
    def total_empty_count(self) -> int:
        return self._total_empty_count

    @property
    def total_string_count(self) -> int:
        return self._total_string_count

    @property
    def total_source_count(self) -> int:
        return self.total_code_count + self.total_string_count

    @property
    def total_file_count(self) -> int:
        return self._total_file_count

    @property
    def total_line_count(self) -> int:
        return self._total_line_count

    def add(self, source_analysis: SourceAnalysis) -> None:
        """
        Add counts from ``source_analysis`` to total counts.
        """
        self._total_file_count += 1
        language_summary = self.language_to_language_summary_map.get(source_analysis.language)
        if language_summary is None:
            language_summary = LanguageSummary(source_analysis.language)
            self.language_to_language_summary_map[source_analysis.language] = language_summary
        language_summary.add(source_analysis)

        if source_analysis.is_countable:
            self._total_code_count += source_analysis.code_count
            self._total_documentation_count += source_analysis.documentation_count
            self._total_empty_count += source_analysis.empty_count
            self._total_line_count += (
                source_analysis.code_count
                + source_analysis.documentation_count
                + source_analysis.empty_count
                + source_analysis.string_count
            )
            self._total_string_count += source_analysis.string_count

    def __repr__(self):
        return "{0}(total_file_count={1}, total_line_count={2}, " "languages={3}".format(
            self.__class__.__name__,
            self.total_file_count,
            self.total_line_count,
            sorted(self.language_to_language_summary_map.keys()),
        )
