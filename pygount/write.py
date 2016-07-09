"""

"""
# Copyright (c) 2016, Thomas Aglassinger.
# All rights reserved. Distributed under the BSD License.
import datetime
import os
from xml.etree import ElementTree


class BaseWriter():
    def __init__(self, target_stream):
        self._target_stream = target_stream
        try:
            self.target_name = self._target_stream.name
        except AttributeError:
            self.target_name = '<io>'
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
        self.total_line_count += \
            source_analysis.code + source_analysis.documentation + source_analysis.empty + source_analysis.string
        self.total_string_count += source_analysis.string

    def close(self):
        self.end_time = datetime.datetime.now()
        self.duration = self.end_time - self.start_time
        self.duration_in_seconds = \
            (1e-6 * self.duration.microseconds) + self.duration.seconds + self.duration.days * 3600 * 24
        if self.duration_in_seconds > 0:
            self.lines_per_second = self.total_line_count / self.duration_in_seconds
            self.sources_per_second = self.total_source_count / self.duration_in_seconds


class LineWriter(BaseWriter):
    """
    Writer that simply writes a line of text for each source code.
    """
    def __init__(self, target_stream):
        super().__init__(target_stream)
        self.template = '{0}\t{1}\t{2}\t{3}'

    def add(self, source_analysis):
        source_line_count = source_analysis.code + source_analysis.string
        line_to_write = self.template.format(
            source_line_count,
            source_analysis.language,
            source_analysis.group,
            source_analysis.path)
        self._target_stream.write(line_to_write + os.linesep)


class ClocXmlWriter(BaseWriter):
    """
    Writer that writes XML output similar to cloc when called with options
    --by-file --xml. This kind of output can be processed by Jenkins' SLOCCount
    plug-in.
    """
    def __init__(self, target_stream):
        super().__init__(target_stream)
        self._results_element = ElementTree.Element('results')
        self._header_element = ElementTree.SubElement(self._results_element, 'header')
        ElementTree.SubElement(self._header_element, 'cloc_url', text='https://github.com/roskakori/pygount')
        ElementTree.SubElement(self._header_element, 'cloc_version', text='1.60')
        self._files_element = ElementTree.SubElement(self._results_element, 'files')

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            # Only write the XML if everything works out.
            self.close()

    def add(self, source_analysis):
        super().add(source_analysis)
        file_attributes = {
            'blank': str(source_analysis.empty),
            'code': str(source_analysis.code + source_analysis.string),
            'comment': str(source_analysis.documentation),
            'language': source_analysis.language,
            'name': source_analysis.path,
        }
        ElementTree.SubElement(self._files_element, 'file', attrib=file_attributes)

    def close(self):
        super().close()
        # Add various statistics to <header>.
        ElementTree.SubElement(self._header_element, 'elapsed_seconds', text='%.f' % self.duration_in_seconds)
        ElementTree.SubElement(self._header_element, 'n_files', text='%d' % self.total_source_count)
        ElementTree.SubElement(self._header_element, 'n_lines', text='%d' % self.total_line_count)
        ElementTree.SubElement(self._header_element, 'files_per_second', text='%.f' % self.sources_per_second)
        ElementTree.SubElement(self._header_element, 'lines_per_second', text='%.f' % self.lines_per_second)
        ElementTree.SubElement(self._header_element, 'report_file', text=self.target_name)

        # Add totals to <files>.
        file_attributes = {
            'blank': str(self.total_empty_count),
            'code': str(self.total_code_count + self.total_string_count),
            'comment': str(self.total_documentation_count),
        }
        ElementTree.SubElement(self._files_element, 'total', attrib=file_attributes)

        # Write the whole XML file.
        if self._target_stream.encoding is not None:
            # Write XML declaration only for files but skip it for io.StringIO.
            self._target_stream.write('<?xml version="1.0" encoding="{0}"?>'.format(self._target_stream.encoding))
        xml_root = ElementTree.ElementTree(self._results_element)
        xml_root.write(self._target_stream, encoding='unicode', xml_declaration=False)
