"""
Tests for function to obtain the language dialect used by XML source code.
"""
# Copyright (c) 2016-2020, Thomas Aglassinger.
# All rights reserved. Distributed under the BSD License.
import os

import pygount.xmldialect

_EXAMPLE_POM_CODE = """<project xmlns="http://maven.apache.org/POM/4.0.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
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
</project>"""

_EXAMPLE_DOCBOOK_DTD_CODE = """<!DOCTYPE example PUBLIC "-//OASIS//DTD DocBook XML V4.1.2//EN"
    "http://www.oasis-open.org/docbook/xml/4.1.2/docbookx.dtd">
<example><title>Hello World in Python</title>
<programlisting>
print('Hello World!')
</programlisting>
</example>
"""


def test_can_detect_ant():
    project_folder = os.path.dirname(os.path.dirname(__file__))
    build_xml_path = os.path.join(project_folder, "build.xml")
    with open(build_xml_path, encoding="utf-8") as build_xml_file:
        build_xml_code = build_xml_file.read()
    assert pygount.xmldialect.xml_dialect(build_xml_path, build_xml_code) == "Ant"


def test_can_detect_maven():
    assert pygount.xmldialect.xml_dialect("<maven>", _EXAMPLE_POM_CODE) == "Maven"


def test_can_ignore_broken_xml():
    assert pygount.xmldialect.xml_dialect("<broken>", "<some></other>") is None


def test_can_detect_docbook_from_dtd():
    assert pygount.xmldialect.xml_dialect("<docbook-dtd>", _EXAMPLE_DOCBOOK_DTD_CODE) == "DocBook XML"
