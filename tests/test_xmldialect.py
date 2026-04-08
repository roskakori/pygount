"""
Tests for function to obtain the language dialect used by XML source code.
"""

import pytest

# Copyright (c) 2016-2024, Thomas Aglassinger.
# All rights reserved. Distributed under the BSD License.
import pygount.xmldialect
from pygount.xmldialect import without_xml_header

EXAMPLE_ANT_CODE = """<project name="hello">
    <target name="hello">
        <echo message="Hello world!" />
    </target>
</project>
"""

_EXAMPLE_POM_CODE = """<project
  xmlns="http://maven.apache.org/POM/4.0.0"
  xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
  xsi:schemaLocation="http://maven.apache.org/POM/4.0.0
  http://maven.apache.org/xsd/maven-4.0.0.xsd">
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

_EXAMPLE_SVG_CODE = (
    '<?xml version="1.0" encoding="UTF-8" standalone="no"?>\n'
    '<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">'
    '<svg xmlns="http://www.w3.org/2000/svg" width="320" height="120" viewBox="0 0 320 120">'
    '  <rect width="100%" height="100%" fill="white"/>'
    '  <text x="50%" y="50%" text-anchor="middle" dominant-baseline="middle" '
    '   font-family="sans-serif" font-size="32" fill="black"'
    "  >Hello, world!</text>"
    "</svg>"
)


@pytest.mark.parametrize(
    "xml_code,expected",
    [
        ("<some/>", "<some/>"),
        ("<some/>", "<some/>"),
        ('<?xml version="1.0"?><some/>', "<some/>"),
        ('  <?xml version="1.0"?><some/>', "<some/>"),
        ('<?xml version="1.0"?>  <some/>', "<some/>"),
        ('\n\n<?xml version="1.0"?>\n\n<some/>', "<some/>"),
    ],
)
def test_can_compute_xml_code_without_header(xml_code: str, expected: str):
    assert without_xml_header(xml_code) == expected


def test_can_detect_ant():
    assert pygount.xmldialect.xml_dialect("<ant>", EXAMPLE_ANT_CODE) == "Ant"


def test_can_detect_maven():
    assert pygount.xmldialect.xml_dialect("<maven>", _EXAMPLE_POM_CODE) == "Maven"


def test_can_ignore_broken_xml():
    assert pygount.xmldialect.xml_dialect("<broken>", "<some></other>") is None


def test_can_detect_docbook_from_dtd():
    assert pygount.xmldialect.xml_dialect("<docbook-dtd>", _EXAMPLE_DOCBOOK_DTD_CODE) == "DocBook XML"


def test_can_detect_svg_from_dtd():
    assert pygount.xmldialect.xml_dialect("<svg>", _EXAMPLE_SVG_CODE) == "SVG XML"
