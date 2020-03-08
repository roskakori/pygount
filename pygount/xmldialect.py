"""
Function to obtain the language dialect used by XML source code.
"""
# Copyright (c) 2016-2020, Thomas Aglassinger.
# All rights reserved. Distributed under the BSD License.
import logging
import re
import xml.sax


# TODO #10: Replace regex for DTD by working DTD handler.
#: Regular expression to obtain DTD.
_DTD_REGEX = re.compile(r'<!DOCTYPE\s+(?P<name>[a-zA-Z][a-zA-Z-]*)\s+PUBLIC\s+"(?P<public_id>.+)"')
_REGEX_PATTERNS_AND_DIALECTS = ((".*DocBook.*", "DocBook XML"),)
_REGEXES_AND_DIALECTS = [(re.compile(pattern), dialect) for pattern, dialect in _REGEX_PATTERNS_AND_DIALECTS]
for public_id_regex, dialect in _REGEX_PATTERNS_AND_DIALECTS:
    assert public_id_regex is not None
    assert dialect is not None
    assert dialect.strip() != ""
#: Regex to detect Sax error messages with uninformative paths like '<unknown>'.
_SAX_MESSAGE_WITHOUT_PATH_PATTERN = re.compile(r"^<.+>(?P<message_without_path>:\d+:\d+.+)")

_log = logging.getLogger("pygount")


class SaxParserDone(Exception):
    """
    Pseudo error to indicate that the Sax parser ist done.
    """

    pass


class XmlDialectHandler(xml.sax.ContentHandler, xml.sax.handler.DTDHandler):
    def __init__(self, max_element_count=100):
        super().__init__()
        self.dialect = None
        self._path = ""
        self._element_count = 0
        self._max_element_count = max_element_count

    def _set_dialect_and_stop_parsing(self, dialect):
        self.dialect = dialect
        raise SaxParserDone("language detected: {0}".format(dialect))

    def startElement(self, name, attrs):
        self._element_count += 1
        if self._element_count == self._max_element_count:
            raise SaxParserDone("no language found after parsing {0} elements".format(self._element_count))
        self._path += "/" + name
        xmlns = attrs.get("xmlns", "")
        if (self._path == "/project") and ("name" in attrs):
            self._set_dialect_and_stop_parsing("Ant")
        elif (self._path in ("/book/title", "/chapter/title")) or (xmlns == "http://docbook.org/ns/docbook"):
            self._set_dialect_and_stop_parsing("DocBook XML")
        elif xmlns == "http://xmlns.jcp.org/xml/ns/javaee":
            self._set_dialect_and_stop_parsing("JavaEE XML")
        elif xmlns.startswith("http://maven.apache.org/POM"):
            self._set_dialect_and_stop_parsing("Maven")
        elif xmlns.startswith("http://www.netbeans.org/ns/project/"):
            self._set_dialect_and_stop_parsing("NetBeans Project")

    def endElement(self, name):
        self._path = self._path[: -len(name) - 1]


def xml_dialect(xml_path, xml_code):
    # TODO #10: Remove hack to obtain DTD using a regex instead of a DTDHandler.
    dtd_match = _DTD_REGEX.match(xml_code)
    if dtd_match is not None:
        public_id = dtd_match.group("public_id")
        for public_id_regex, dialect in _REGEXES_AND_DIALECTS:
            if public_id_regex.match(public_id):
                return dialect

    xml_dialect_handler = XmlDialectHandler()
    parser = xml.sax.make_parser()
    parser.setContentHandler(xml_dialect_handler)
    parser.setFeature(xml.sax.handler.feature_external_ges, False)
    parser.setFeature(xml.sax.handler.feature_external_pes, False)
    parser.setFeature(xml.sax.handler.feature_validation, False)
    try:
        parser.feed(xml_code)
        # NOTE: We can only call close() when the parser has finished,
        # otherwise close() raises a SAXException('parser finished').
        parser.close()
    except SaxParserDone:
        # Language has been determined or the parser has given up.
        pass
    except (ValueError, xml.sax.SAXException) as error:
        # NOTE: ValueError is raised on unknown url type.
        error_message = str(error)
        message_without_path_match = _SAX_MESSAGE_WITHOUT_PATH_PATTERN.match(error_message)
        if message_without_path_match is not None:
            # HACK: Replace uninformative sax path like '<unknown>' with actual XML path.
            error_message = xml_path + message_without_path_match.group("message_without_path")
        _log.warning(error_message)
    except OSError as error:
        _log.warning("%s: cannot analyze XML dialect: %s", xml_path, error)
    return xml_dialect_handler.dialect
