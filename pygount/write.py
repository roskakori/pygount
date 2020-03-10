"""
Writers to store the resuls of a pygount analysis.
"""
# Copyright (c) 2016-2020, Thomas Aglassinger.
# All rights reserved. Distributed under the BSD License.
import datetime
import functools
import math
import os
from xml.etree import ElementTree

from pygount.analysis import SourceState


class BaseWriter:
    def __init__(self, target_stream):
        self._target_stream = target_stream
        try:
            self.target_name = self._target_stream.name
        except AttributeError:
            self.target_name = "<io>"
        self.source_count = 0
        self.start_time = datetime.datetime.now()
        self.end_time = None
        self.total_code_count = 0
        self.total_documentation_count = 0
        self.total_empty_count = 0
        self.total_string_count = 0
        self.total_source_count = 0
        self.total_line_count = 0
        self.sources_per_second = 0
        self.lines_per_second = 0
        self.duration = None
        self.duration_in_seconds = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def add(self, source_analysis):
        self.total_code_count += source_analysis.code
        self.total_documentation_count += source_analysis.documentation
        self.total_empty_count += source_analysis.empty
        self.total_source_count += 1
        self.total_line_count += (
            source_analysis.code + source_analysis.documentation + source_analysis.empty + source_analysis.string
        )
        self.total_string_count += source_analysis.string

    def close(self):
        self.end_time = datetime.datetime.now()
        self.duration = self.end_time - self.start_time
        self.duration_in_seconds = (
            (1e-6 * self.duration.microseconds) + self.duration.seconds + self.duration.days * 3600 * 24
        )
        if self.duration_in_seconds > 0:
            self.lines_per_second = self.total_line_count / self.duration_in_seconds
            self.sources_per_second = self.total_source_count / self.duration_in_seconds


class LineWriter(BaseWriter):
    """
    Writer that simply writes a line of text for each source code.
    """

    def __init__(self, target_stream):
        super().__init__(target_stream)
        self.template = "{0}\t{1}\t{2}\t{3}"

    def add(self, source_analysis):
        source_line_count = source_analysis.code + source_analysis.string
        line_to_write = self.template.format(
            source_line_count, source_analysis.language, source_analysis.group, source_analysis.path
        )
        self._target_stream.write(line_to_write + os.linesep)


class ClocXmlWriter(BaseWriter):
    """
    Writer that writes XML output similar to cloc when called with options
    --by-file --xml. This kind of output can be processed by Jenkins' SLOCCount
    plug-in.
    """

    def __init__(self, target_stream):
        super().__init__(target_stream)
        self._results_element = ElementTree.Element("results")
        self._header_element = ElementTree.SubElement(self._results_element, "header")
        ElementTree.SubElement(self._header_element, "cloc_url", text="https://github.com/roskakori/pygount")
        ElementTree.SubElement(self._header_element, "cloc_version", text="1.60")
        self._files_element = ElementTree.SubElement(self._results_element, "files")

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            # Only write the XML if everything works out.
            self.close()

    def add(self, source_analysis):
        super().add(source_analysis)
        file_attributes = {
            "blank": str(source_analysis.empty),
            "code": str(source_analysis.code + source_analysis.string),
            "comment": str(source_analysis.documentation),
            "language": source_analysis.language,
            "name": source_analysis.path,
        }
        ElementTree.SubElement(self._files_element, "file", attrib=file_attributes)

    def close(self):
        super().close()
        # Add various statistics to <header>.
        ElementTree.SubElement(self._header_element, "elapsed_seconds", text="%.f" % self.duration_in_seconds)
        ElementTree.SubElement(self._header_element, "n_files", text="%d" % self.total_source_count)
        ElementTree.SubElement(self._header_element, "n_lines", text="%d" % self.total_line_count)
        ElementTree.SubElement(self._header_element, "files_per_second", text="%.f" % self.sources_per_second)
        ElementTree.SubElement(self._header_element, "lines_per_second", text="%.f" % self.lines_per_second)
        ElementTree.SubElement(self._header_element, "report_file", text=self.target_name)

        # Add totals to <files>.
        file_attributes = {
            "blank": str(self.total_empty_count),
            "code": str(self.total_code_count + self.total_string_count),
            "comment": str(self.total_documentation_count),
        }
        ElementTree.SubElement(self._files_element, "total", attrib=file_attributes)

        # Write the whole XML file.
        if self._target_stream.encoding is not None:
            # Write XML declaration only for files but skip it for io.StringIO.
            self._target_stream.write('<?xml version="1.0" encoding="{0}"?>'.format(self._target_stream.encoding))
        xml_root = ElementTree.ElementTree(self._results_element)
        xml_root.write(self._target_stream, encoding="unicode", xml_declaration=False)


#: Language statistics collected by ``SummaryWriter``.
@functools.total_ordering
class _LanguageStatistics:
    def __init__(self, language):
        self.language = language
        self.code = 0
        self.documentation = 0
        self.empty = 0
        self.string = 0

    def sort_key(self):
        return self.code, self.documentation, self.string, self.empty, self.language

    def __eq__(self, other):
        return self.sort_key() == other.sort_key()

    def __lt__(self, other):
        return self.sort_key() < other.sort_key()


class SummaryWriter(BaseWriter):
    """
    Writer to summarize the analysis per language in a format that can easily
    be read by humans.
    """

    _LANGUAGE_HEADING = "Language"
    _CODE_HEADING = "Code"
    _DOCUMENTATION_HEADING = "Comment"
    _SUM_TOTAL_PSEUDO_LANGUAGE = "Sum total"

    def __init__(self, target_stream):
        super().__init__(target_stream)
        self._language_to_language_statistics_map = {}
        self._max_language_width = max(
            len(SummaryWriter._LANGUAGE_HEADING), len(SummaryWriter._SUM_TOTAL_PSEUDO_LANGUAGE)
        )
        self._max_code_width = 0
        self._max_documentation_width = 0

    def add(self, source_analysis):
        super().add(source_analysis)
        if source_analysis.state in (SourceState.analyzed.name, SourceState.duplicate.name):
            language_statistics = self._language_to_language_statistics_map.get(source_analysis.language)
            if language_statistics is None:
                language_statistics = _LanguageStatistics(source_analysis.language)
                self._language_to_language_statistics_map[source_analysis.language] = language_statistics
            language_statistics.code += source_analysis.code
            language_statistics.documentation += source_analysis.documentation
            language_statistics.empty += source_analysis.empty
            language_statistics.string += source_analysis.string

    def close(self):
        super().close()

        # Compute maximum column widths
        max_language_width = max(len(SummaryWriter._LANGUAGE_HEADING), len(SummaryWriter._SUM_TOTAL_PSEUDO_LANGUAGE),)
        max_code_width = len(SummaryWriter._CODE_HEADING)
        max_documentation_width = len(SummaryWriter._DOCUMENTATION_HEADING)
        for language, language_statistics in self._language_to_language_statistics_map.items():
            language_width = len(language)
            if language_width > max_language_width:
                max_language_width = language_width
            code_width = digit_width(language_statistics.code)
            if code_width > max_code_width:
                max_code_width = code_width
            documentation_width = digit_width(language_statistics.documentation)
            if documentation_width > max_documentation_width:
                max_documentation_width = documentation_width
        percentage_width = 6
        digits_after_dot = 2
        max_digits_before_dot = percentage_width - digits_after_dot - 1
        assert max_digits_before_dot >= 3  # Must be able to hold "100".

        summary_heading = (
            "{0:^{max_language_width}s}  "
            "{1:^{max_code_width}s}  "
            "{2:^{percentage_width}s}  "
            "{3:^{max_documentation_width}s}  "
            "{2:^{percentage_width}s}"
        ).format(
            SummaryWriter._LANGUAGE_HEADING,
            SummaryWriter._CODE_HEADING,
            "%",
            SummaryWriter._DOCUMENTATION_HEADING,
            max_documentation_width=max_documentation_width,
            max_language_width=max_language_width,
            max_code_width=max_code_width,
            percentage_width=percentage_width,
        )
        self._target_stream.write(summary_heading + os.linesep)
        separator_line = "  ".join(
            [
                "-" * width
                for width in (
                    max_language_width,
                    max_code_width,
                    percentage_width,
                    max_documentation_width,
                    percentage_width,
                )
            ]
        )
        self._target_stream.write(separator_line + os.linesep)
        language_line_template = (
            "{0:{max_language_width}s}  "
            "{1:>{max_code_width}d}  "
            "{2:>{percentage_width}.0{digits_after_dot}f}  "
            "{3:>{max_documentation_width}d}  "
            "{4:>{percentage_width}.0{digits_after_dot}f}"
        )
        for language_statistics in sorted(self._language_to_language_statistics_map.values(), reverse=True):
            code_count = language_statistics.code
            code_percentage = code_count / self.total_code_count * 100 if self.total_code_count != 0 else 0.0
            documentation_percentage = (
                language_statistics.documentation / self.total_documentation_count * 100
                if self.total_documentation_count != 0
                else 0.0
            )
            line_to_write = language_line_template.format(
                language_statistics.language,
                code_count,
                code_percentage,
                language_statistics.documentation,
                documentation_percentage,
                digits_after_dot=digits_after_dot,
                max_documentation_width=max_documentation_width,
                max_language_width=max_language_width,
                max_code_width=max_code_width,
                percentage_width=percentage_width,
            )
            self._target_stream.write(line_to_write + os.linesep)
        self._target_stream.write(separator_line + os.linesep)
        summary_footer = (
            "{0:{max_language_width}s}  "
            "{1:>{max_code_width}d}  "
            "{2:{percentage_width}s}  "
            "{3:>{max_documentation_width}d}"
        ).format(
            SummaryWriter._SUM_TOTAL_PSEUDO_LANGUAGE,
            self.total_code_count,
            "",
            self.total_documentation_count,
            max_documentation_width=max_documentation_width,
            max_language_width=max_language_width,
            max_code_width=max_code_width,
            percentage_width=percentage_width,
        )
        self._target_stream.write(summary_footer + os.linesep)


def digit_width(line_count):
    assert line_count >= 0
    return math.ceil(math.log10(line_count + 1)) if line_count != 0 else 1
