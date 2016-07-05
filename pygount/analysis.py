"""
Count lines of code using pygments.
"""
# Copyright (c) 2016, Thomas Aglassinger.
# All rights reserved. Distributed under the BSD License.
import codecs
import collections
import re

import chardet.universaldetector
from pygments import lexers, token, util

import pygount

_log = pygount.log
_detector = chardet.universaldetector.UniversalDetector()

_MARK_TO_NAME_MAP = (
    ('c', 'code'),
    ('d', 'documentation'),
    ('e', 'empty'),
    ('s', 'string'),
)
_BOM_TO_ENCODING_MAP = collections.OrderedDict((
    # NOTE: We need an ordered dict due the overlap between utf-32-le and utf-16-be.
    (codecs.BOM_UTF8, 'utf-8-sig'),
    (codecs.BOM_UTF32_LE, 'utf-32-le'),
    (codecs.BOM_UTF16_BE, 'utf-16-be'),
    (codecs.BOM_UTF16_LE, 'utf-16-le'),
    (codecs.BOM_UTF32_BE, 'utf-32-be'),
))
_XML_PROLOG_REGEX = re.compile(r'<\?xml\s+.*encoding="(?P<encoding>[-_.a-zA-Z0-9]+)".*\?>')
_CODING_MAGIC_REGEX = re.compile(r'.+coding[:=][ \t]*(?P<encoding>[-_.a-zA-Z0-9]+)\b', re.DOTALL)

LineAnalysis = collections.namedtuple(
    'LineAnalysis', ['path', 'language', 'group', 'code', 'documentation', 'empty', 'string'])


def _delined_tokens(tokens):
    for token_type, token_text in tokens:
        newline_index = token_text.find('\n')
        while newline_index != -1:
            yield token_type, token_text[:newline_index + 1]
            token_text = token_text[newline_index + 1:]
            newline_index = token_text.find('\n')
        if token_text != '':
            yield token_type, token_text


def _pythonized_comments(tokens):
    """
    Similar to tokens but converts strings after a colon (:) to comments.
    """
    is_after_colon = True
    for token_type, token_text in tokens:
        if is_after_colon and (token_type in token.String):
            token_type = token.Comment
        elif token_text == ':':
            is_after_colon = True
        elif token_type not in token.Comment:
            is_whitespace = len(token_text.rstrip(' \f\n\r\t')) == 0
            if not is_whitespace:
                is_after_colon = False
        yield token_type, token_text


def _line_parts(lexer, text):
    line_marks = set()
    tokens = _delined_tokens(lexer.get_tokens(text))
    if lexer.name == 'Python':
        tokens = _pythonized_comments(tokens)
    for token_type, token_text in tokens:
        if token_type in token.Comment:
            line_marks.add('d')  # 'documentation'
        elif token_type in token.String:
            line_marks.add('s')  # 'string'
        else:
            is_whitespace = len(token_text.rstrip(' \f\n\r\t')) == 0
            if not is_whitespace:
                line_marks.add('c')  # 'code'
        if token_text.endswith('\n'):
            yield line_marks
            line_marks = set()
    if len(line_marks) >= 1:
        yield line_marks


def encoding_for(source_path, encoding='automatic', fallback_encoding='cp1252'):
    assert encoding is not None
    assert fallback_encoding is not None

    if encoding == 'automatic':
        with open(source_path, 'rb') as source_file:
            heading = source_file.read(128)
        result = None
        if len(heading) == 0:
            # File is empty, assume a dummy encoding.
            result = 'utf-8'
        if result is None:
            # Check for known BOMs.
            for bom, encoding in _BOM_TO_ENCODING_MAP.items():
                if heading[:len(bom)] == bom:
                    result = encoding
                    break
        if result is None:
            # Look for common headings that indicate the encoding.
            ascii_heading = heading.decode('ascii', errors='replace')
            ascii_heading = ascii_heading.replace('\r\n', '\n')
            ascii_heading = ascii_heading.replace('\r', '\n')
            ascii_heading = '\n'.join(ascii_heading.split('\n')[:2]) + '\n'
            coding_magic_match = _CODING_MAGIC_REGEX.match(ascii_heading)
            if coding_magic_match is not None:
                result = coding_magic_match.group('encoding')
            else:
                first_line = ascii_heading.split('\n')[0]
                xml_prolog_match = _XML_PROLOG_REGEX.match(first_line)
                if xml_prolog_match is not None:
                    result = xml_prolog_match.group('encoding')
        if result is None:
            try:
                # Attempt to read the first 16 KiB of the file as UTF-8.
                with open(source_path, 'r', encoding='utf-8') as source_file:
                    source_file.read(16384)
                result = 'utf-8'
            except UnicodeDecodeError:
                # It is not UTF-8, just assume the fallback encoding.
                result = fallback_encoding
    elif encoding == 'chardet':
        _detector.reset()
        with open(source_path, 'rb') as source_file:
            for line in source_file.readlines():
                _detector.feed(line)
                if _detector.done:
                    break
        result = _detector.result['encoding']
    else:
        # Simply use the specified encoding.
        result = encoding
    assert result is not None
    return result


def source_analysis(source_path, group, encoding='automatic', fallback_encoding='cp1252'):
    assert encoding is not None
    assert fallback_encoding is not None

    result = None
    try:
        lexer = lexers.get_lexer_for_filename(source_path)
    except util.ClassNotFound:
        lexer = None
    if lexer is not None:
        if encoding == 'automatic':
            encoding = encoding_for(source_path, encoding, fallback_encoding)
        _log.info('%s: analyze as %s using encoding %s', source_path, lexer.name, encoding)
        try:
            with open(source_path, 'r', encoding=encoding) as source_file:
                text = source_file.read()
        except (OSError, UnicodeDecodeError) as error:
            _log.warning('cannot read %s: %s', source_path, error)
            result = LineAnalysis(source_path, 'error', group, 0, 0, 0, 0)
        if result is None:
            mark_to_count_map = {'c': 0, 'd': 0, 'e': 0, 's': 0}
            for line_parts in _line_parts(lexer, text):
                mark_to_increment = 'e'
                for mark_to_check in ('d', 's', 'c'):
                    if mark_to_check in line_parts:
                        mark_to_increment = mark_to_check
                mark_to_count_map[mark_to_increment] += 1
            result = LineAnalysis(
                path=source_path,
                language=lexer.name,
                group=group,
                code=mark_to_count_map['c'],
                documentation=mark_to_count_map['d'],
                empty=mark_to_count_map['e'],
                string=mark_to_count_map['s']
            )
    else:
        _log.info('%s: skip', source_path)
        result = LineAnalysis(source_path, None, group, 0, 0, 0, 0)

    assert result is not None
    return result
