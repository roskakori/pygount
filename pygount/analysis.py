"""
Count lines of code using pygments.
"""
import collections

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

LineAnalysis = collections.namedtuple(
    'LineAnalysis', ['path', 'language', 'project', 'code', 'documentation', 'empty', 'string'])


def _delined_tokens(tokens):
    for token_type, token_text in tokens:
        newline_index = token_text.find('\n')
        while newline_index != -1:
            yield token_type, token_text[:newline_index + 1]
            token_text = token_text[newline_index + 1:]
            newline_index = token_text.find('\n')
        if token_text != '':
            yield token_type, token_text


def _line_parts(lexer, text):
    line_marks = set()
    for token_type, token_text in _delined_tokens(lexer.get_tokens(text)):
        if token_type in token.Comment:
            line_marks.add('d')  # 'documentation'
        elif token_type in token.String:
            line_marks.add('s')  # 'string'
        elif (token_type != token.Whitespace) and (token_text != '\n'):
            line_marks.add('c')  # 'code'
        if token_text.endswith('\n'):
            yield line_marks
            line_marks = set()
    if len(line_marks) >= 1:
        yield line_marks


def _encoding_for(source_path):
    with open(source_path, 'rb') as source_file:
        for line in source_file.readlines():
            _detector.feed(line)
            if _detector.done:
                break
    return _detector.result['encoding']


def line_analysis(project, source_path, encoding=None):
    result = None
    try:
        lexer = lexers.get_lexer_for_filename(source_path)
    except util.ClassNotFound:
        lexer = None
    if lexer is not None:
        if encoding is None:
            encoding = _encoding_for(source_path)
        _log.info('%s: analyze as %s using encoding %s', source_path, lexer.name, encoding)
        try:
            with open(source_path, 'r', encoding=encoding) as source_file:
                    text = source_file.read()
        except (OSError, UnicodeDecodeError) as error:
            _log.warning('cannot read %s: %s', source_path, error)
            result = LineAnalysis(source_path, 'error', project, 0, 0, 0, 0)
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
                project=project,
                code=mark_to_count_map['c'],
                documentation=mark_to_count_map['d'],
                empty=mark_to_count_map['e'],
                string=mark_to_count_map['s']
            )
    else:
        _log.info('%s: skip', source_path)
        result = LineAnalysis(source_path, None, project, 0, 0, 0, 0)

    assert result is not None
    return result
