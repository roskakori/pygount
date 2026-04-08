"""
Writers to store the results of a pygount analysis.
"""

# Copyright (c) 2016-2024, Thomas Aglassinger.
# All rights reserved. Distributed under the BSD License.
import datetime
import json
import math
import os
from xml.etree import ElementTree

from rich.console import Console
from rich.table import Table

import pygount

from . import SourceAnalysis
from .summary import ProjectSummary

#: Version of cloc the --format=cloc-xml pretends to be.
CLOC_VERSION = "1.60"

JSON_FORMAT_VERSION = "1.1.0"


class BaseWriter:
    def __init__(self, target_stream, **kwargs):
        self._target_stream = target_stream
        try:
            self.target_name = self._target_stream.name
        except AttributeError:
            self.target_name = "<io>"
        self.project_summary = ProjectSummary()
        self.started_at = self._utc_now()
        self.finished_at = None
        self.files_per_second = 0
        self.lines_per_second = 0
        self.duration = None
        self.duration_in_seconds = 0.0
        self.has_to_track_progress = True

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        return False

    def add(self, source_analysis):
        self.project_summary.add(source_analysis)

    def close(self):
        self.project_summary.update_file_percentages()
        self.finished_at = self._utc_now()
        self.duration = self.finished_at - self.started_at
        self.duration_in_seconds = max(
            0.001, self.duration.microseconds * 1e-6 + self.duration.seconds + self.duration.days * 3600 * 24
        )
        self.lines_per_second = self.project_summary.total_line_count / self.duration_in_seconds
        self.files_per_second = self.project_summary.total_file_count / self.duration_in_seconds

    @staticmethod
    def _utc_now() -> datetime.datetime:
        # After switching to Python 3.11+, we can change this to `now(datetime.UTC)`.
        return datetime.datetime.now(datetime.timezone.utc)


class LineWriter(BaseWriter):
    """
    Writer that simply writes a line of text for each source code.
    """

    def __init__(self, target_stream, **kwargs):
        super().__init__(target_stream, **kwargs)
        self.has_to_track_progress = False

    def add(self, source_analysis):
        source_line_count = source_analysis.code_count + source_analysis.string_count
        line_to_write = (
            f"{source_line_count}\t{source_analysis.language}\t{source_analysis.group}\t{source_analysis.path}"
        )
        self._target_stream.write(line_to_write + os.linesep)


class ClocXmlWriter(BaseWriter):
    """
    Writer that writes XML output similar to cloc when called with options
    --by-file --xml. This kind of output can be processed by Jenkins' SLOCCount
    plug-in.
    """

    def __init__(self, target_stream, **kwargs):
        super().__init__(target_stream, **kwargs)
        self._results_element = ElementTree.Element("results")
        self._header_element = ElementTree.SubElement(self._results_element, "header")
        ElementTree.SubElement(self._header_element, "cloc_url", text="https://github.com/roskakori/pygount")
        ElementTree.SubElement(self._header_element, "cloc_version", text=CLOC_VERSION)
        self._files_element = ElementTree.SubElement(self._results_element, "files")

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            # Only write the XML if everything works out.
            self.close()

    def add(self, source_analysis: SourceAnalysis):
        super().add(source_analysis)
        file_attributes = {
            "blank": str(source_analysis.empty_count),
            "code": str(source_analysis.source_count),
            "comment": str(source_analysis.documentation_count),
            "language": source_analysis.language,
            "name": source_analysis.path,
        }
        ElementTree.SubElement(self._files_element, "file", attrib=file_attributes)

    def close(self):
        super().close()
        # Add various statistics to <header>.
        ElementTree.SubElement(self._header_element, "elapsed_seconds", text=str(self.duration_in_seconds))
        ElementTree.SubElement(self._header_element, "n_files", text=str(self.project_summary.total_file_count))
        ElementTree.SubElement(self._header_element, "n_lines", text=str(self.project_summary.total_line_count))
        ElementTree.SubElement(self._header_element, "files_per_second", text=f"{self.files_per_second:f}")
        ElementTree.SubElement(self._header_element, "lines_per_second", text=f"{self.lines_per_second:f}")
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
            self._target_stream.write(f'<?xml version="1.0" encoding="{self._target_stream.encoding}"?>')
        xml_root = ElementTree.ElementTree(self._results_element)
        xml_root.write(self._target_stream, encoding="unicode", xml_declaration=False)


class SummaryWriter(BaseWriter):
    """
    Writer to summarize the analysis per language in a format that can easily
    be read by humans.
    """

    _COLUMNS_WITH_JUSTIFY = (
        ("Language", "left"),
        ("Files", "right"),
        ("%", "right"),
        ("Code", "right"),
        ("%", "right"),
        ("Comment", "right"),
        ("%", "right"),
    )

    def close(self):
        super().close()

        table = Table()
        for column, justify in self._COLUMNS_WITH_JUSTIFY:
            table.add_column(column, justify=justify, overflow="fold")

        language_summaries = sorted(self.project_summary.language_to_language_summary_map.values(), reverse=True)
        for index, language_summary in enumerate(language_summaries, start=1):
            table.add_row(
                language_summary.language,
                str(language_summary.file_count),
                formatted_percentage(language_summary.file_percentage),
                str(language_summary.code_count),
                formatted_percentage(language_summary.code_percentage),
                str(language_summary.documentation_count),
                formatted_percentage(language_summary.documentation_percentage),
                end_section=(index == len(language_summaries)),
            )
        table.add_row(
            "Sum",
            str(self.project_summary.total_file_count),
            formatted_percentage(100.0),
            str(self.project_summary.total_code_count),
            formatted_percentage(self.project_summary.total_code_percentage),
            str(self.project_summary.total_documentation_count),
            formatted_percentage(self.project_summary.total_documentation_percentage),
        )
        Console(file=self._target_stream, soft_wrap=True).print(table)


class JsonWriter(BaseWriter):
    """
    Writer JSON output, ideal for further automatic processing.
    """

    def __init__(self, target_stream, **kwargs):
        super().__init__(target_stream, **kwargs)
        self.source_analyses = []

    def add(self, source_analysis: SourceAnalysis):
        super().add(source_analysis)
        self.source_analyses.append(
            {
                "codeCount": source_analysis.code_count,
                "documentationCount": source_analysis.documentation_count,
                "emptyCount": source_analysis.empty_count,
                "group": source_analysis.group,
                "isCountable": source_analysis.is_countable,
                "language": source_analysis.language,
                "lineCount": source_analysis.line_count,
                "path": source_analysis.path,
                "state": source_analysis.state.name,
                "stateInfo": source_analysis.state_info,
                "sourceCount": source_analysis.source_count,
            }
        )

    def close(self):
        # NOTE: JSON names use camel case to follow JSLint's guidelines, see <https://www.jslint.com/>.
        super().close()
        json_map = {
            "formatVersion": JSON_FORMAT_VERSION,
            "pygountVersion": pygount.__version__,
            "files": self.source_analyses,
            "languages": [
                {
                    "documentationCount": language_summary.documentation_count,
                    "documentationPercentage": language_summary.documentation_percentage,
                    "codeCount": language_summary.code_count,
                    "codePercentage": language_summary.code_percentage,
                    "emptyCount": language_summary.empty_count,
                    "emptyPercentage": language_summary.empty_percentage,
                    "fileCount": language_summary.file_count,
                    "filePercentage": language_summary.file_percentage,
                    "isPseudoLanguage": language_summary.is_pseudo_language,
                    "language": language_summary.language,
                    "sourceCount": language_summary.source_count,
                    "sourcePercentage": language_summary.source_percentage,
                    "stringCount": language_summary.string_count,
                    "stringPercentage": language_summary.string_percentage,
                }
                for language_summary in self.project_summary.language_to_language_summary_map.values()
            ],
            "runtime": {
                "durationInSeconds": self.duration_in_seconds,
                "filesPerSecond": self.files_per_second,
                "finishedAt": self.finished_at.isoformat(),
                "linesPerSecond": self.lines_per_second,
                "startedAt": self.started_at.isoformat(),
            },
            "summary": {
                "totalCodeCount": self.project_summary.total_code_count,
                "totalCodePercentage": self.project_summary.total_code_percentage,
                "totalDocumentationCount": self.project_summary.total_documentation_count,
                "totalDocumentationPercentage": self.project_summary.total_documentation_percentage,
                "totalEmptyCount": self.project_summary.total_empty_count,
                "totalEmptyPercentage": self.project_summary.total_empty_percentage,
                "totalFileCount": self.project_summary.total_file_count,
                "totalSourceCount": self.project_summary.total_source_count,
                "totalSourcePercentage": self.project_summary.total_source_percentage,
                "totalStringCount": self.project_summary.total_string_count,
                "totalStringPercentage": self.project_summary.total_string_percentage,
            },
        }
        json.dump(json_map, self._target_stream)


class GraphWriter(BaseWriter):
    """
    Writer that generates an SVG chart showing SLOC per language over git tags.
    """

    def __init__(self, target_stream, **kwargs):
        super().__init__(target_stream, **kwargs)
        colors_text = kwargs.get("colors", "")
        self._colors = ["#" + c.strip().lstrip("#") for c in colors_text.split(",") if c.strip().lstrip("#")]
        self._width = kwargs.get("width", 1024)
        self._height = kwargs.get("height", 768)
        self._tag_names = []
        self._tag_to_language_sloc = {}
        self._languages = set()

    def add(self, source_analysis: SourceAnalysis):
        super().add(source_analysis)
        tag = source_analysis.group
        if tag not in self._tag_to_language_sloc:
            self._tag_to_language_sloc[tag] = {}
            self._tag_names.append(tag)
        lang = source_analysis.language
        self._languages.add(lang)
        sloc = source_analysis.code_count + source_analysis.string_count
        self._tag_to_language_sloc[tag][lang] = self._tag_to_language_sloc[tag].get(lang, 0) + sloc

    def close(self):
        super().close()
        if not self._tag_names:
            return

        # Sort languages by total SLOC across all tags.
        lang_totals = {
            lang: sum(self._tag_to_language_sloc[tag].get(lang, 0) for tag in self._tag_names)
            for lang in self._languages
        }
        sorted_langs = sorted(self._languages, key=lambda l: lang_totals[l], reverse=True)

        # Parameters for the chart.
        margin_left = 80
        margin_right = 150
        margin_top = 50
        margin_bottom = 80
        chart_width = self._width - margin_left - margin_right
        chart_height = self._height - margin_top - margin_bottom

        max_sloc = 0
        for tag in self._tag_names:
            total = sum(self._tag_to_language_sloc[tag].values())
            max_sloc = max(max_sloc, total)
        if max_sloc == 0:
            max_sloc = 1

        # Start SVG.
        svg = [
            f'<svg width="{self._width}" height="{self._height}" xmlns="http://www.w3.org/2000/svg">',
            '<rect width="100%" height="100%" fill="white"/>',
        ]

        # Draw axes.
        svg.append(
            f'<line x1="{margin_left}" y1="{margin_top}" x2="{margin_left}" y2="{self._height - margin_bottom}" stroke="black"/>'
        )
        svg.append(
            f'<line x1="{margin_left}" y1="{self._height - margin_bottom}" x2="{self._width - margin_right}" y2="{self._height - margin_bottom}" stroke="black"/>'
        )

        num_tags = len(self._tag_names)
        x_step = chart_width / (num_tags - 1) if num_tags > 1 else chart_width

        # Draw stacked areas.
        prev_y = [self._height - margin_bottom] * num_tags
        for i, lang in enumerate(sorted_langs):
            color = self._colors[i % len(self._colors)]
            points = []
            new_prev_y = []
            for j, tag in enumerate(self._tag_names):
                x = margin_left + j * x_step
                sloc = self._tag_to_language_sloc[tag].get(lang, 0)
                y = prev_y[j] - (sloc / max_sloc * chart_height)
                points.append(f"{x},{y}")
                new_prev_y.append(y)

            # Area path.
            path_points = points + [
                f"{margin_left + (num_tags - 1) * x_step},{prev_y[-1]}",
                f"{margin_left},{prev_y[0]}",
            ]
            svg.append(f'<polygon points="{" ".join(path_points)}" fill="{color}" opacity="0.8"/>')
            prev_y = new_prev_y

            # Legend.
            legend_x = self._width - margin_right + 10
            legend_y = margin_top + i * 20
            svg.append(f'<rect x="{legend_x}" y="{legend_y}" width="15" height="15" fill="{color}"/>')
            svg.append(
                f'<text x="{legend_x + 20}" y="{legend_y + 12}" font-family="sans-serif" font-size="12">{lang}</text>'
            )

        # Draw tag labels.
        for j, tag in enumerate(self._tag_names):
            x = margin_left + j * x_step
            svg.append(
                f'<text x="{x}" y="{self._height - margin_bottom + 20}" font-family="sans-serif" font-size="10" text-anchor="middle" transform="rotate(45 {x},{self._height - margin_bottom + 20})">{tag}</text>'
            )

        # Y axis labels.
        for i in range(6):
            val = int(max_sloc * i / 5)
            y = self._height - margin_bottom - (i / 5 * chart_height)
            svg.append(
                f'<text x="{margin_left - 5}" y="{y + 4}" font-family="sans-serif" font-size="10" text-anchor="end">{val}</text>'
            )

        svg.append("</svg>")
        self._target_stream.write("\n".join(svg))


def digit_width(line_count: int) -> int:
    assert line_count >= 0
    return math.ceil(math.log10(line_count + 1)) if line_count != 0 else 1


def formatted_percentage(percentage: float) -> str:
    assert percentage >= 0.0
    assert percentage <= 100.0
    return f"{percentage:.01f}"
