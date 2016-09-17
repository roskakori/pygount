"""
Test to write results of pygount analyses.
"""
# Copyright (c) 2016, Thomas Aglassinger.
# All rights reserved. Distributed under the BSD License.
import io
import tempfile
import unittest
from xml.etree import ElementTree

from pygount import analysis
from pygount import write


class BaseWriterCase(unittest.TestCase):
    def test_can_collect_totals(self):
        source_analyses = (
            analysis.SourceAnalysis(
                'some.py', 'Python', 'some', 1, 2, 3, 4, analysis.SourceState.analyzed.name, None),
            analysis.SourceAnalysis(
                'other.py', 'Python', 'some', 10, 20, 30, 40,  analysis.SourceState.analyzed.name, None),
        )
        with tempfile.NamedTemporaryFile('w', encoding='utf-8', prefix='pygount_', suffix='.tmp') as target_stream:
            with write.BaseWriter(target_stream) as writer:
                for source_analysis in source_analyses:
                    writer.add(source_analysis)
        self.assertEqual(writer.total_source_count, 2)
        self.assertEqual(writer.total_line_count, 110)


class ClocXmlWriterTest(unittest.TestCase):
    def test_can_write_cloc_xml(self):
        source_analyses = (
            analysis.SourceAnalysis(
                'some.py', 'Python', 'some', 1, 2, 3, 4, analysis.SourceState.analyzed.name, None),
            analysis.SourceAnalysis(
                'other.py', 'Python', 'some', 10, 20, 30, 40,  analysis.SourceState.analyzed.name, None),
        )
        with io.StringIO() as target_stream:
            with write.ClocXmlWriter(target_stream) as writer:
                for source_analysis in source_analyses:
                    writer.add(source_analysis)
            xml_data = target_stream.getvalue()
            self.assertNotEqual(len(xml_data), 0)
        with io.StringIO(xml_data) as cloc_xml_stream:
            cloc_results_root = ElementTree.parse(cloc_xml_stream)
        file_elements = cloc_results_root.findall('files/file')
        self.assertIsNotNone(file_elements)
        self.assertEqual(len(file_elements), len(source_analyses))


if __name__ == '__main__':
    unittest.main()
