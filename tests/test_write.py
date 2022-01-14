"""
Test to write results of pygount analyses.
"""
# Copyright (c) 2016-2022, Thomas Aglassinger.
# All rights reserved. Distributed under the BSD License.
import io
from pathlib import Path
import tempfile
from collections import namedtuple
from xml.etree import ElementTree

from pygount import analysis, write

from ._common import TempFolderTest


def test_can_collect_totals():
    source_analyses = (
        analysis.SourceAnalysis("some.py", "Python", "some", 1, 2, 3, 4, analysis.SourceState.analyzed, None),
        analysis.SourceAnalysis("other.py", "Python", "some", 10, 20, 30, 40, analysis.SourceState.analyzed, None),
    )
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", prefix="pygount_", suffix=".tmp") as target_stream:
        with write.BaseWriter(target_stream) as writer:
            for source_analysis in source_analyses:
                writer.add(source_analysis)
    assert writer.project_summary.total_file_count == 2
    assert writer.project_summary.total_line_count == 110
    assert writer.duration_in_seconds > 0
    assert writer.lines_per_second > writer.files_per_second


def test_can_write_cloc_xml():
    source_analyses = (
        analysis.SourceAnalysis("some.py", "Python", "some", 1, 2, 3, 4, analysis.SourceState.analyzed, None),
        analysis.SourceAnalysis("other.py", "Python", "some", 10, 20, 30, 40, analysis.SourceState.analyzed, None),
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
    "_LineData",
    [
        "language",
        "file_count",
        "blank_count",
        "comment_count",
        "code_count",
    ],
)


def _line_data_from(line):
    line_parts = [word for word in line.split() if word.isalnum()]
    assert len(line_parts) == 5, f"line_parts={line_parts}"
    return _LineData(
        line_parts[0],
        int(line_parts[1]),
        int(line_parts[2]),
        int(line_parts[3]),
        int(line_parts[4]),
    )


class SummaryWriterTest(TempFolderTest):
    def test_can_write_summary(self):
        source_analyses = (
            analysis.SourceAnalysis("script.sh", "Bash", "some", 200, 25, 1, 2, analysis.SourceState.analyzed, None),
            analysis.SourceAnalysis("some.py", "Python", "some", 300, 45, 3, 4, analysis.SourceState.analyzed, None),
            analysis.SourceAnalysis("other.py", "Python", "some", 500, 30, 5, 6, analysis.SourceState.analyzed, None),
        )
        lines = self._summary_lines_for(source_analyses)
        assert len(lines) == 8, f"lines={lines}"

        python_data = _line_data_from(lines[3])
        assert python_data.language == "Python"
        assert python_data.file_count == 2
        assert python_data.code_count == 800
        assert python_data.comment_count == 75

        bash_data = _line_data_from(lines[4])
        assert bash_data.language == "Bash"
        assert bash_data.file_count == 1
        assert bash_data.code_count == 200
        assert bash_data.comment_count == 25

        sum_total_data = [word.strip() for word in lines[-2].split("│") if word]
        assert len(sum_total_data) >= 3
        assert sum_total_data[-2:] == ["100", "1000"]

    def _summary_lines_for(self, source_analyses):
        # NOTE: We need to write to a file because the lines containing the
        # actual data are only during close() at which point they would not be
        # accessible to StringIO.getvalue().
        summary_path = Path(self.tests_temp_folder, "summary.tmp")
        with summary_path.open("w", encoding="utf-8") as summary_file:
            with write.SummaryWriter(summary_file) as writer:
                for source_analysis in source_analyses:
                    writer.add(source_analysis)
        return summary_path.read_text("utf-8").splitlines()
