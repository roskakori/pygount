"""
Test to write results of pygount analyses.
"""
# Copyright (c) 2016-2020, Thomas Aglassinger.
# All rights reserved. Distributed under the BSD License.
import io
import os
import tempfile
from collections import namedtuple

import pytest
from xml.etree import ElementTree

from pygount import analysis
from pygount import write
from tests._common import TempFolderTest


def test_can_collect_totals():
    source_analyses = (
        analysis.SourceAnalysis("some.py", "Python", "some", 1, 2, 3, 4, analysis.SourceState.analyzed.name, None),
        analysis.SourceAnalysis("other.py", "Python", "some", 10, 20, 30, 40, analysis.SourceState.analyzed.name, None),
    )
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", prefix="pygount_", suffix=".tmp") as target_stream:
        with write.BaseWriter(target_stream) as writer:
            for source_analysis in source_analyses:
                writer.add(source_analysis)
    assert writer.total_source_count == 2
    assert writer.total_line_count == 110


def test_can_write_cloc_xml():
    source_analyses = (
        analysis.SourceAnalysis("some.py", "Python", "some", 1, 2, 3, 4, analysis.SourceState.analyzed.name, None),
        analysis.SourceAnalysis("other.py", "Python", "some", 10, 20, 30, 40, analysis.SourceState.analyzed.name, None),
    )
    with io.StringIO() as target_stream:
        with write.ClocXmlWriter(target_stream) as writer:
            for source_analysis in source_analyses:
                writer.add(source_analysis)
        xml_data = target_stream.getvalue()
        assert len(xml_data) >= 1
    with io.StringIO(xml_data) as cloc_xml_stream:
        cloc_results_root = ElementTree.parse(cloc_xml_stream)
    file_elements = cloc_results_root.findall("files/file")
    assert file_elements is not None
    assert len(file_elements) == len(source_analyses)


def test_can_compute_digit_width():
    assert write.digit_width(0) == 1
    assert write.digit_width(1) == 1
    assert write.digit_width(9) == 1
    assert write.digit_width(999) == 3
    assert write.digit_width(1000) == 4


_LineData = namedtuple(
    "_LineData", ["language", "code_count", "code_percent", "documentation_count", "documentation_percent"]
)


def _line_data_from(line):
    line_parts = line.split()
    assert len(line_parts) == 5, "line_parts={0}".format(line_parts)
    return _LineData(line_parts[0], int(line_parts[1]), float(line_parts[2]), int(line_parts[3]), float(line_parts[4]),)


class SummaryWriterTest(TempFolderTest):
    def test_can_write_summary(self):
        source_analyses = (
            analysis.SourceAnalysis(
                "script.sh", "Bash", "some", 200, 25, 1, 2, analysis.SourceState.analyzed.name, None
            ),
            analysis.SourceAnalysis(
                "some.py", "Python", "some", 300, 45, 3, 4, analysis.SourceState.analyzed.name, None
            ),
            analysis.SourceAnalysis(
                "other.py", "Python", "some", 500, 30, 5, 6, analysis.SourceState.analyzed.name, None
            ),
        )
        lines = self._summary_lines_for(source_analyses)
        assert len(lines) == 6, "lines={}".format(lines)

        python_data = _line_data_from(lines[2])
        assert python_data.language == "Python"
        assert python_data.code_count == 800
        assert python_data.documentation_count == 75
        assert python_data.code_percent == pytest.approx(80.0)
        assert python_data.documentation_percent == pytest.approx(75.0)

        bash_data = _line_data_from(lines[3])
        assert bash_data.language == "Bash"
        assert bash_data.code_count == 200
        assert bash_data.documentation_count == 25
        assert bash_data.code_percent == pytest.approx(20.0)
        assert bash_data.documentation_percent == pytest.approx(25.0)

        sum_total_data = lines[-1].split()
        assert len(sum_total_data) >= 3
        assert sum_total_data[-2:] == ["1000", "100"]

    def _summary_lines_for(self, source_analyses):
        # NOTE: We need to write to a file because the lines containing the
        # actual data are only during close() at which point they would not be
        # accessible to StringIO.getvalue().
        summary_path = os.path.join(self.tests_temp_folder, "summary.tmp")
        with open(summary_path, "w", encoding="utf-8") as target_summary_file:
            with write.SummaryWriter(target_summary_file) as writer:
                for source_analysis in source_analyses:
                    writer.add(source_analysis)
        with open(summary_path, "r", encoding="utf-8") as source_summary_file:
            result = [line.rstrip("\n") for line in source_summary_file]
        return result

    def test_can_format_data_longer_than_headings(self):
        huge_number = int("1234567890" * 10)
        long_language_name = "x" * 100
        min_line_length = len(long_language_name) + 2 * write.digit_width(huge_number)

        source_analyses = (
            analysis.SourceAnalysis(
                "x",
                long_language_name,
                "some",
                huge_number,
                huge_number,
                0,
                0,
                analysis.SourceState.analyzed.name,
                None,
            ),
        )
        for line in self._summary_lines_for(source_analyses):
            assert len(line) > min_line_length, "line={0}".format(line)
