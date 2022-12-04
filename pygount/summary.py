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
        self._file_percentage = 0.0
        self._string_count = 0
        self._is_pseudo_language = _PSEUDO_LANGUAGE_REGEX.match(self.language) is not None
        self._has_up_to_date_percentages = False

    @property
    def language(self) -> str:
        """the language to be summarized"""
        return self._language

    @property
    def code_count(self) -> int:
        """sum lines of code for this language"""
        return self._code_count

    @property
    def code_percentage(self) -> float:
        """percentage of lines containing code for this language across entire project"""
        return _percentage_or_0(self.code_count, self.line_count)

    def _assert_has_up_to_date_percentages(self):
        assert self._has_up_to_date_percentages, "update_percentages() must be called first"

    @property
    def documentation_count(self) -> int:
        """sum lines of documentation for this language"""
        return self._documentation_count

    @property
    def documentation_percentage(self) -> float:
        """percentage of lines containing documentation for this language across entire project"""
        return _percentage_or_0(self.documentation_count, self.line_count)

    @property
    def empty_count(self) -> int:
        """sum empty lines for this language"""
        return self._empty_count

    @property
    def empty_percentage(self) -> float:
        """percentage of empty lines for this language across entire project"""
        return _percentage_or_0(self.empty_count, self.line_count)

    @property
    def file_count(self) -> int:
        """number of source code files for this language"""
        return self._file_count

    @property
    def file_percentage(self) -> float:
        """percentage of files in project"""
        self._assert_has_up_to_date_percentages()
        return self._file_percentage

    @property
    def line_count(self) -> int:
        """sum count of all lines of any kind for this language"""
        return self.code_count + self.documentation_count + self.empty_count + self.string_count

    @property
    def string_count(self) -> int:
        """sum number of lines containing strings for this language"""
        return self._string_count

    @property
    def string_percentage(self) -> float:
        """percentage of lines containing strings for this language across entire project"""
        return _percentage_or_0(self.string_count, self.line_count)

    @property
    def source_count(self) -> int:
        """sum number of source lines of code"""
        return self.code_count + self.string_count

    @property
    def source_percentage(self) -> float:
        """percentage of source lines for code for this language across entire project"""
        return _percentage_or_0(self.source_count, self.line_count)

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

        self._has_up_to_date_percentages = False
        self._file_count += 1
        if source_analysis.is_countable:
            self._code_count += source_analysis.code_count
            self._documentation_count += source_analysis.documentation_count
            self._empty_count += source_analysis.empty_count
            self._string_count += source_analysis.string_count

    def update_file_percentage(self, project_summary: "ProjectSummary"):
        self._file_percentage = _percentage_or_0(self.file_count, project_summary.total_file_count)
        self._has_up_to_date_percentages = True

    def __repr__(self):
        result = f"{self.__class__.__name__}(language={self.language!r}, file_count={self.file_count}"
        if not self.is_pseudo_language:
            result += ", code_count={}, documentation_count={}, empty_count={}, string_count={}".format(
                self.code_count, self.documentation_count, self.empty_count, self.string_count
            )
        result += ")"
        return result


def _percentage_or_0(partial_count: int, total_count: int) -> float:
    assert partial_count >= 0
    assert total_count >= 0
    return 100 * partial_count / total_count if total_count != 0 else 0.0


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
    def total_code_percentage(self) -> float:
        return _percentage_or_0(self.total_code_count, self.total_line_count)

    @property
    def total_documentation_count(self) -> int:
        return self._total_documentation_count

    @property
    def total_documentation_percentage(self) -> float:
        return _percentage_or_0(self.total_documentation_count, self.total_line_count)

    @property
    def total_empty_count(self) -> int:
        return self._total_empty_count

    @property
    def total_empty_percentage(self) -> float:
        return _percentage_or_0(self.total_empty_count, self.total_line_count)

    @property
    def total_string_count(self) -> int:
        return self._total_string_count

    @property
    def total_string_percentage(self) -> float:
        return _percentage_or_0(self.total_string_count, self.total_line_count)

    @property
    def total_source_count(self) -> int:
        return self.total_code_count + self.total_string_count

    @property
    def total_source_percentage(self) -> float:
        return _percentage_or_0(self.total_source_count, self.total_line_count)

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

    def update_file_percentages(self) -> None:
        """Update percentages for all languages part of the project."""
        for language_summary in self._language_to_language_summary_map.values():
            language_summary.update_file_percentage(self)

    def __repr__(self):
        return (
            f"{self.__class__.__name__}("
            f"total_file_count={self.total_file_count}, "
            f"total_line_count={self.total_line_count}, "
            f"languages={sorted(self.language_to_language_summary_map.keys())})"
        )
