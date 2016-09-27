"""
Function to obtain the language dialect used by XML source code.
"""
# Copyright (c) 2016, Thomas Aglassinger.
# All rights reserved. Distributed under the BSD License.
import logging
import xml.sax


_log = logging.getLogger('pygount')


class SaxParserDone(Exception):
    """
    Pseudo error to indicate that the Sax parser ist done.
    """
    pass


class XmlDialectContentHandler(xml.sax.ContentHandler):
    def __init__(self, max_element_count=100):
        super().__init__()
        self.dialect = None
        self._path = ''
        self._element_count = 0
        self._max_element_count = max_element_count

    def _set_dialect(self, dialect):
        self.dialect = dialect
        raise SaxParserDone('language detected: {0}'.format(dialect))

    def startElement(self, name, attrs):
        self._element_count += 1
        if self._element_count == self._max_element_count:
            raise SaxParserDone('no language found after parsing {0} elements'.format(self._element_count))
        self._path += '/' + name
        xmlns = attrs.get('xmlns', '')
        if (self._path == '/project') and ('name' in attrs):
            self._set_dialect('Ant')
        elif (self._path in ('/book/title', '/chapter/title')) or (xmlns == 'http://docbook.org/ns/docbook'):
            self._set_dialect('DocBook XML')
        elif xmlns == 'http://xmlns.jcp.org/xml/ns/javaee':
            self._set_dialect('JavaEE XML')
        elif xmlns.startswith('http://maven.apache.org/POM'):
            self._set_dialect('Maven')
        elif xmlns.startswith('http://www.netbeans.org/ns/project/'):
            self._set_dialect('NetBeans Project')

    def startElementNS(self, name, qname, attrs):
        self.startElement(name, attrs)

    def endElement(self, name):
        self._path = self._path[:-len(name) - 1]

    def endElementNS(self, name, qname):
        self.endElement(name)


def xml_dialect(xml_path):
    content_handler = XmlDialectContentHandler()
    parser = xml.sax.make_parser()
    parser.setContentHandler(content_handler)
    parser.setFeature(xml.sax.handler.feature_external_ges, False)
    parser.setFeature(xml.sax.handler.feature_external_pes, False)
    parser.setFeature(xml.sax.handler.feature_validation, False)
    try:
        parser.parse(xml_path)
    except SaxParserDone:
        # Language has been determined or the parser has given up.
        pass
    except (ValueError, xml.sax.SAXException) as error:
        # NOTE: ValueError is raised on unknown url type.
        _log.warning(error)  # error already includes path
    except OSError as error:
        _log.warning('%s: cannot analyze XML dialect: %s', xml_path, error)
    return content_handler.dialect
