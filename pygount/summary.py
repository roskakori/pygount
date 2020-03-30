"""
Summaries of analyses of multiple source codes.
"""
# Copyright (c) 2016-2020, Thomas Aglassinger.
# All rights reserved. Distributed under the BSD License.
import functools
import re

from .analysis import SourceAnalysis


_PSEUDO_LANGUAGE_REGEX = re.compile("^__[a-z]+__$")


@functools.total_ordering
class LanguageSummary:
    """
    Summary of a source code counts from multiple files of the same language.
    """

    def __init__(self, language: str):
        self.language = language
        self.code = 0
        self.documentation = 0
        self.file_count = 0
        self.empty = 0
        self.string = 0
        self.is_pseudo_language = _PSEUDO_LANGUAGE_REGEX.match(self.language) is not None

    def sort_key(self):
        return self.code, self.documentation, self.string, self.empty, self.language

    def __eq__(self, other):
        return self.sort_key() == other.sort_key()

    def __lt__(self, other):
        return self.sort_key() < other.sort_key()

    def add(self, source_analysis: SourceAnalysis):
        self.file_count += 1
        if source_analysis.is_countable:
            self.code += source_analysis.code
            self.documentation += source_analysis.documentation
            self.empty += source_analysis.empty
            self.string += source_analysis.string

    def __repr__(self):
        result = "{0}(language={1!r}, file_count={2}".format(self.__class__.__name__, self.language, self.file_count)
        if not self.is_pseudo_language:
            result += ", code={0}, documentation={1}, empty={2}, string={3}".format(
                self.code, self.documentation, self.empty, self.string
            )
        result += ")"
        return result


class ProjectSummary:
    """
    Summary of source code counts for several languages and files.
    """

    def __init__(self):
        self.language_to_language_summary_map = {}
        self.total_code_count = 0
        self.total_documentation_count = 0
        self.total_empty_count = 0
        self.total_string_count = 0
        self.total_file_count = 0
        self.total_line_count = 0

    def add(self, source_analysis: SourceAnalysis):
        self.total_file_count += 1
        language_summary = self.language_to_language_summary_map.get(source_analysis.language)
        if language_summary is None:
            language_summary = LanguageSummary(source_analysis.language)
            self.language_to_language_summary_map[source_analysis.language] = language_summary
        language_summary.add(source_analysis)

        if source_analysis.is_countable:
            self.total_code_count += source_analysis.code
            self.total_documentation_count += source_analysis.documentation
            self.total_empty_count += source_analysis.empty
            self.total_line_count += (
                source_analysis.code + source_analysis.documentation + source_analysis.empty + source_analysis.string
            )
            self.total_string_count += source_analysis.string

    def __repr__(self):
        return "{0}(total_file_count={1}, total_line_count={2}, " "languages={3}".format(
            self.__class__.__name__,
            self.total_file_count,
            self.total_line_count,
            sorted(self.language_to_language_summary_map.keys()),
        )
