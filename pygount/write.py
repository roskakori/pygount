"""
Writers to store the resuls of a pygount analysis.
"""
# Copyright (c) 2016-2020, Thomas Aglassinger.
# All rights reserved. Distributed under the BSD License.
import datetime
import math
import os
from xml.etree import ElementTree

from .summary import ProjectSummary


class BaseWriter:
    def __init__(self, target_stream):
        self._target_stream = target_stream
        try:
            self.target_name = self._target_stream.name
        except AttributeError:
            self.target_name = "<io>"
        self.project_summary = ProjectSummary()
        self.start_time = datetime.datetime.now()
        self.end_time = None
        self.sources_per_second = 0
        self.lines_per_second = 0
        self.duration = None
        self.duration_in_seconds = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def add(self, source_analysis):
        self.project_summary.add(source_analysis)

    def close(self):
        self.end_time = datetime.datetime.now()
        self.duration = self.end_time - self.start_time
        self.duration_in_seconds = (
            (1e-6 * self.duration.microseconds) + self.duration.seconds + self.duration.days * 3600 * 24
        )
        if self.duration_in_seconds > 0:
            self.lines_per_second = self.project_summary.total_file_count / self.duration_in_seconds
            self.sources_per_second = self.project_summary.total_file_count / self.duration_in_seconds


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
        ElementTree.SubElement(self._header_element, "n_files", text="%d" % self.project_summary.total_file_count)
        ElementTree.SubElement(self._header_element, "n_lines", text="%d" % self.project_summary.total_line_count)
        ElementTree.SubElement(self._header_element, "files_per_second", text="%.f" % self.sources_per_second)
        ElementTree.SubElement(self._header_element, "lines_per_second", text="%.f" % self.lines_per_second)
        ElementTree.SubElement(self._header_element, "report_file", text=self.target_name)

        # Add totals to <files>.
        file_attributes = {
            "blank": str(self.project_summary.total_empty_count),
            "code": str(self.project_summary.total_code_count + self.project_summary.total_string_count),
            "comment": str(self.project_summary.total_documentation_count),
        }
        ElementTree.SubElement(self._files_element, "total", attrib=file_attributes)

        # Write the whole XML file.
        if self._target_stream.encoding is not None:
            # Write XML declaration only for files but skip it for io.StringIO.
            self._target_stream.write('<?xml version="1.0" encoding="{0}"?>'.format(self._target_stream.encoding))
        xml_root = ElementTree.ElementTree(self._results_element)
        xml_root.write(self._target_stream, encoding="unicode", xml_declaration=False)


class SummaryWriter(BaseWriter):
    """
    Writer to summarize the analysis per language in a format that can easily
    be read by humans.
    """

    _LANGUAGE_HEADING = "Language"
    _FILE_COUNT_HEADING = "Files"
    _CODE_HEADING = "Code"
    _DOCUMENTATION_HEADING = "Comment"
    _SUM_TOTAL_PSEUDO_LANGUAGE = "Sum total"
    _PERCENTAGE_DIGITS_AFTER_DOT = 2

    def __init__(self, target_stream):
        super().__init__(target_stream)
        self._max_language_width = max(
            len(SummaryWriter._LANGUAGE_HEADING), len(SummaryWriter._SUM_TOTAL_PSEUDO_LANGUAGE)
        )
        self._max_code_width = 0
        self._max_documentation_width = 0

    def close(self):
        super().close()

        # Compute maximum column widths
        max_language_width = max(len(SummaryWriter._LANGUAGE_HEADING), len(SummaryWriter._SUM_TOTAL_PSEUDO_LANGUAGE),)
        max_file_count_width = len(SummaryWriter._FILE_COUNT_HEADING)
        max_code_width = len(SummaryWriter._CODE_HEADING)
        max_documentation_width = len(SummaryWriter._DOCUMENTATION_HEADING)
        for language, language_summary in self.project_summary.language_to_language_summary_map.items():
            language_width = len(language)
            if language_width > max_language_width:
                max_language_width = language_width
            file_count_width = digit_width(language_summary.file_count)
            if file_count_width > max_file_count_width:
                max_file_count_width = file_count_width
            code_width = digit_width(language_summary.code)
            if code_width > max_code_width:
                max_code_width = code_width
            documentation_width = digit_width(language_summary.documentation)
            if documentation_width > max_documentation_width:
                max_documentation_width = documentation_width
        digits_after_dot = self._PERCENTAGE_DIGITS_AFTER_DOT
        percentage_width = 4 + digits_after_dot  # To represent "100." we need 4 characters.

        summary_heading = (
            "{0:^{max_language_width}s}  "
            "{1:^{max_file_count_width}s}  "
            "{2:^{percentage_width}s}  "
            "{3:^{max_code_width}s}  "
            "{2:^{percentage_width}s}  "
            "{4:^{max_documentation_width}s}  "
            "{2:^{percentage_width}s}"
        ).format(
            SummaryWriter._LANGUAGE_HEADING,
            SummaryWriter._FILE_COUNT_HEADING,
            "%",
            SummaryWriter._CODE_HEADING,
            SummaryWriter._DOCUMENTATION_HEADING,
            max_code_width=max_code_width,
            max_file_count_width=max_file_count_width,
            max_documentation_width=max_documentation_width,
            max_language_width=max_language_width,
            percentage_width=percentage_width,
        )
        self._target_stream.write(summary_heading + os.linesep)
        separator_line = "  ".join(
            [
                "-" * width
                for width in (
                    max_language_width,
                    max_file_count_width,
                    percentage_width,
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
            "{1:>{max_file_count_width}d}  "
            "{2:>{percentage_width}.0{digits_after_dot}f}  "
            "{3:>{max_code_width}d}  "
            "{4:>{percentage_width}.0{digits_after_dot}f}  "
            "{5:>{max_documentation_width}d}  "
            "{6:>{percentage_width}.0{digits_after_dot}f}"
        )
        for language_summary in sorted(self.project_summary.language_to_language_summary_map.values(), reverse=True):
            code_count = language_summary.code
            code_percentage = (
                code_count / self.project_summary.total_code_count * 100
                if self.project_summary.total_code_count != 0
                else 0.0
            )
            file_count = language_summary.file_count
            assert (
                self.project_summary.total_file_count != 0
            ), "if there is at least 1 language summary, there must be a file count too"
            file_percentage = file_count / self.project_summary.total_file_count * 100
            documentation_percentage = (
                language_summary.documentation / self.project_summary.total_documentation_count * 100
                if self.project_summary.total_documentation_count != 0
                else 0.0
            )
            line_to_write = language_line_template.format(
                language_summary.language,
                file_count,
                file_percentage,
                code_count,
                code_percentage,
                language_summary.documentation,
                documentation_percentage,
                digits_after_dot=digits_after_dot,
                max_code_width=max_code_width,
                max_documentation_width=max_documentation_width,
                max_file_count_width=max_file_count_width,
                max_language_width=max_language_width,
                percentage_width=percentage_width,
            )
            self._target_stream.write(line_to_write + os.linesep)
        self._target_stream.write(separator_line + os.linesep)
        summary_footer = (
            "{0:{max_language_width}s}  "
            "{1:>{max_file_count_width}d}  "
            "{2:{percentage_width}s}  "
            "{3:>{max_code_width}d}  "
            "{2:{percentage_width}s}  "
            "{4:>{max_documentation_width}d}"
        ).format(
            SummaryWriter._SUM_TOTAL_PSEUDO_LANGUAGE,
            self.project_summary.total_file_count,
            "",
            self.project_summary.total_code_count,
            self.project_summary.total_documentation_count,
            max_documentation_width=max_documentation_width,
            max_file_count_width=max_file_count_width,
            max_language_width=max_language_width,
            max_code_width=max_code_width,
            percentage_width=percentage_width,
        )
        self._target_stream.write(summary_footer + os.linesep)


def digit_width(line_count):
    assert line_count >= 0
    return math.ceil(math.log10(line_count + 1)) if line_count != 0 else 1
