"""
Tests for function to obtain the language dialect used by XML source code.
"""
# Copyright (c) 2016, Thomas Aglassinger.
# All rights reserved. Distributed under the BSD License.
import os
import tempfile
import unittest

import pygount.xmldialect
from tests.test_analysis import _test_path


_EXAMPLE_POM_CODE = '''<project xmlns="http://maven.apache.org/POM/4.0.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
  xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 http://maven.apache.org/xsd/maven-4.0.0.xsd">
  <modelVersion>4.0.0</modelVersion>

  <groupId>com.mycompany.app</groupId>
  <artifactId>my-app</artifactId>
  <version>1.0-SNAPSHOT</version>
  <packaging>jar</packaging>

  <name>Maven Quick Start Archetype</name>
  <url>http://maven.apache.org</url>

  <dependencies>
    <dependency>
      <groupId>junit</groupId>
      <artifactId>junit</artifactId>
      <version>4.8.2</version>
      <scope>test</scope>
    </dependency>
  </dependencies>
</project>'''


class XmlLanguageTest(unittest.TestCase):
    def test_can_detect_ant(self):
        project_folder = os.path.dirname(os.path.dirname(__file__))
        build_xml_path = os.path.join(project_folder, 'build.xml')
        self.assertEqual(pygount.xmldialect.xml_dialect(build_xml_path), 'Ant')

    def test_can_detect_maven(self):
        pom_xml_path = _test_path('pom', 'xml')
        with open(pom_xml_path, 'w', encoding='utf-8') as pom_xml_file:
            pom_xml_file.write(_EXAMPLE_POM_CODE)
        self.assertEqual(pygount.xmldialect.xml_dialect(pom_xml_path), 'Maven')

    def test_can_ignore_broken_xml(self):
        broken_xml_path = _test_path('broken', 'xml')
        with open(broken_xml_path, 'w', encoding='utf-8') as broken_xml_file:
            broken_xml_file.write('<some></other>')
        self.assertEqual(pygount.xmldialect.xml_dialect(broken_xml_path), None)

    def test_can_ignore_non_existent_xml(self):
        non_existent_xml_path = os.path.join(tempfile.gettempdir(), 'missing_folder', 'non_existent.xml')
        self.assertEqual(pygount.xmldialect.xml_dialect(non_existent_xml_path), None)
