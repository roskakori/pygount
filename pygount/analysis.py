"""
Functions to analyze source code and count lines in it.
"""
# Copyright (c) 2016-2020, Thomas Aglassinger.
# All rights reserved. Distributed under the BSD License.
import codecs
import collections
import enum
import glob
import hashlib
import itertools
import logging
import os
import re

import pygments.lexer
import pygments.lexers
import pygments.token
import pygments.util

import pygount.common
import pygount.lexers
import pygount.xmldialect

# Attempt to import chardet.
try:
    import chardet.universaldetector

    _detector = chardet.universaldetector.UniversalDetector()
except ImportError:
    _detector = None
has_chardet = bool(_detector)

#: Fallback encoding to use if no encoding is specified
DEFAULT_FALLBACK_ENCODING = "cp1252"

#: Default glob patterns for folders not to analyze.
DEFAULT_FOLDER_PATTERNS_TO_SKIP_TEXT = ", ".join(
    [".*", "_svn", "__pycache__"]  # Subversion hack for Windows  # Python byte code
)

SourceState = enum.Enum(
    "SourceState",
    " ".join(
        [
            "analyzed",  # successfully analyzed
            "binary",  # source code is a binary
            "duplicate",  # source code is an identical copy of another
            "empty",  # source code is empty (file size = 0)
            "error",  # source could not be parsed
            "generated",  # source code has been generated
            # TODO: 'huge',  # source code exceeds size limit
            "unknown",  # pygments does not offer any lexer to analyze the source
        ]
    ),
)

#: Default patterns for regular expressions to detect generated code.
#: The '(?i)' indicates that the patterns are case insensitive.
DEFAULT_GENERATED_PATTERNS_TEXT = pygount.common.REGEX_PATTERN_PREFIX + ", ".join(
    [
        r"(?i).*automatically generated",
        r"(?i).*do not edit",
        r"(?i).*generated with the .+ utility",
        r"(?i).*this is a generated file",
        r"(?i).*generated automatically",
    ]
)

#: Default glob patterns for file names not to analyze.
DEFAULT_NAME_PATTERNS_TO_SKIP_TEXT = ", ".join([".*", "*~"])

_log = logging.getLogger("pygount")

_MARK_TO_NAME_MAP = (("c", "code"), ("d", "documentation"), ("e", "empty"), ("s", "string"))
_BOM_TO_ENCODING_MAP = collections.OrderedDict(
    (
        # NOTE: We need an ordered dict due to the overlap between utf-32-le and utf-16-be.
        (codecs.BOM_UTF8, "utf-8-sig"),
        (codecs.BOM_UTF32_LE, "utf-32-le"),
        (codecs.BOM_UTF16_BE, "utf-16-be"),
        (codecs.BOM_UTF16_LE, "utf-16-le"),
        (codecs.BOM_UTF32_BE, "utf-32-be"),
    )
)
_XML_PROLOG_REGEX = re.compile(r'<\?xml\s+.*encoding="(?P<encoding>[-_.a-zA-Z0-9]+)".*\?>')
_CODING_MAGIC_REGEX = re.compile(r".+coding[:=][ \t]*(?P<encoding>[-_.a-zA-Z0-9]+)\b", re.DOTALL)

_STANDARD_PLAIN_TEXT_NAMES = (
    # Text files for (moribund) gnits standards.
    "authors",
    "bugs",
    "changelog",
    "copying",
    "install",
    "license",
    "news",
    "readme",
    "thanks",
    # Other common text files.
    "changes",
    "faq",
    "readme\\.1st",
    "read\\.me",
    "todo",
    ".*\\.txt",
)
_PLAIN_TEXT_PATTERN = "(^" + "$)|(^".join(_STANDARD_PLAIN_TEXT_NAMES) + "$)"
#: Regular expression to detect plain text files by name.
_PLAIN_TEXT_NAME_REGEX = re.compile(_PLAIN_TEXT_PATTERN, re.IGNORECASE)

#: Results of a source analysis derived by :py:func:`source_analysis`.
SourceAnalysis = collections.namedtuple(
    "SourceAnalysis", ["path", "language", "group", "code", "documentation", "empty", "string", "state", "state_info"]
)

#: Mapping for file suffixes to lexers for which pygments offers no official one.
_SUFFIX_TO_FALLBACK_LEXER_MAP = {
    "fex": pygount.lexers.MinimalisticWebFocusLexer(),
    "idl": pygount.lexers.IdlLexer(),
    "m4": pygount.lexers.MinimalisticM4Lexer(),
    "vbe": pygount.lexers.MinimalisticVBScriptLexer(),
    "vbs": pygount.lexers.MinimalisticVBScriptLexer(),
}
for oracle_suffix in ("pck", "pkb", "pks", "pls"):
    _SUFFIX_TO_FALLBACK_LEXER_MAP[oracle_suffix] = pygments.lexers.get_lexer_by_name("plpgsql")


class SourceScanner:
    def __init__(
        self,
        source_patterns,
        suffixes="*",
        folders_to_skip=pygount.common.regexes_from(DEFAULT_FOLDER_PATTERNS_TO_SKIP_TEXT),
        name_to_skip=pygount.common.regexes_from(DEFAULT_NAME_PATTERNS_TO_SKIP_TEXT),
    ):
        self._source_patterns = source_patterns
        self._suffixes = pygount.common.regexes_from(suffixes)
        self._folder_regexps_to_skip = folders_to_skip
        self._name_regexps_to_skip = name_to_skip

    @property
    def source_patterns(self):
        return self._source_patterns

    @property
    def suffixes(self):
        return self._suffixes

    @property
    def folder_regexps_to_skip(self):
        return self._folder_regexps_to_skip

    @folder_regexps_to_skip.setter
    def set_folder_pattern_to_skip(self, regexps_or_pattern_text):
        self._folder_regexps_to_skip.append = pygount.common.regexes_from(
            regexps_or_pattern_text, self.folder_regexps_to_skip
        )

    @property
    def name_regexps_to_skip(self):
        return self._name_regexps_to_skip

    @name_regexps_to_skip.setter
    def set_name_regexps_to_skip(self, regexps_or_pattern_text):
        self._name_regexp_to_skip = pygount.common.regexes_from(regexps_or_pattern_text, self.name_regexps_to_skip)

    def _is_path_to_skip(self, name, is_folder):
        assert os.sep not in name, "name=%r" % name
        regexps_to_skip = self._folder_regexps_to_skip if is_folder else self._name_regexps_to_skip
        return any(path_name_to_skip_regex.match(name) is not None for path_name_to_skip_regex in regexps_to_skip)

    def _paths_and_group_to_analyze_in(self, folder, group):
        assert folder is not None
        assert group is not None

        for name in os.listdir(folder):
            path = os.path.join(folder, name)
            if not os.path.islink(path):
                is_folder = os.path.isdir(path)
                if self._is_path_to_skip(os.path.basename(path), is_folder):
                    _log.debug("skip due to matching skip pattern: %s", path)
                elif is_folder:
                    yield from self._paths_and_group_to_analyze_in(path, group)
                else:
                    yield path, group

    def _paths_and_group_to_analyze(self, path_to_analyse_pattern, group=None):
        for path_to_analyse in glob.glob(path_to_analyse_pattern):
            if os.path.islink(path_to_analyse):
                _log.debug("skip link: %s", path_to_analyse)
            else:
                is_folder = os.path.isdir(path_to_analyse)
                if self._is_path_to_skip(os.path.basename(path_to_analyse), is_folder):
                    _log.debug("skip due to matching skip pattern: %s", path_to_analyse)
                else:
                    actual_group = group
                    if is_folder:
                        if actual_group is None:
                            actual_group = os.path.basename(path_to_analyse)
                            if actual_group == "":
                                # Compensate for trailing path separator.
                                actual_group = os.path.basename(os.path.dirname(path_to_analyse))
                        yield from self._paths_and_group_to_analyze_in(path_to_analyse_pattern, actual_group)
                    else:
                        if actual_group is None:
                            actual_group = os.path.dirname(path_to_analyse)
                            if actual_group == "":
                                actual_group = os.path.basename(os.path.dirname(os.path.abspath(path_to_analyse)))
                        yield path_to_analyse, actual_group

    def _source_paths_and_groups_to_analyze(self, patterns_to_analyze):
        assert patterns_to_analyze is not None
        result = []
        for pattern in patterns_to_analyze:
            try:
                result.extend(self._paths_and_group_to_analyze(pattern))
            except OSError as error:
                raise OSError('cannot scan "{0}" for source files: {1}'.format(pattern, error))
        result = sorted(set(result))
        return result

    def source_paths(self):
        source_paths_and_groups_to_analyze = self._source_paths_and_groups_to_analyze(self.source_patterns)

        for source_path, group in source_paths_and_groups_to_analyze:
            suffix = os.path.splitext(source_path)[1].lstrip(".")
            is_suffix_to_analyze = any(suffix_regexp.match(suffix) for suffix_regexp in self.suffixes)
            if is_suffix_to_analyze:
                yield source_path, group
            else:
                _log.info("skip due to suffix: %s", source_path)


_LANGUAGE_TO_WHITE_WORDS_MAP = {"batchfile": ["@"], "python": ["pass"], "sql": ["begin", "end"]}
for language in _LANGUAGE_TO_WHITE_WORDS_MAP.keys():
    assert language.islower()


def matching_number_line_and_regex(source_lines, generated_regexes, max_line_count=15):
    """
    The first line and its number (starting with 0) in the source code that
    indicated that the source code is generated.
    :param source_lines: lines of text to scan
    :param generated_regexes: regular expressions a line must match to indicate
        the source code is generated.
    :param max_line_count: maximum number of lines to scan
    :return: a tuple of the form ``(number, line, regex)`` or ``None`` if the
        source lines do not match any ``generated_regexes``.
    """
    initial_numbers_and_lines = enumerate(itertools.islice(source_lines, max_line_count))
    matching_number_line_and_regexps = (
        (number, line, matching_regex)
        for number, line in initial_numbers_and_lines
        for matching_regex in generated_regexes
        if matching_regex.match(line)
    )
    possible_first_matching_number_line_and_regexp = list(itertools.islice(matching_number_line_and_regexps, 1))
    result = (possible_first_matching_number_line_and_regexp + [None])[0]
    return result


def white_characters(language_id):
    """
    Characters that count as white space if they are the only characters in a
    line.
    """
    assert language_id is not None
    assert language_id.islower()
    return "(),:;[]{}"


def white_code_words(language_id):
    """
    Words that do not count as code if it is the only word in a line.
    """
    assert language_id is not None
    assert language_id.islower()
    return _LANGUAGE_TO_WHITE_WORDS_MAP.get(language_id, set())


def _delined_tokens(tokens):
    for token_type, token_text in tokens:
        newline_index = token_text.find("\n")
        while newline_index != -1:
            yield token_type, token_text[: newline_index + 1]
            token_text = token_text[newline_index + 1 :]
            newline_index = token_text.find("\n")
        if token_text != "":
            yield token_type, token_text


def _pythonized_comments(tokens):
    """
    Similar to tokens but converts strings after a colon (:) to comments.
    """
    is_after_colon = True
    for token_type, token_text in tokens:
        if is_after_colon and (token_type in pygments.token.String):
            token_type = pygments.token.Comment
        elif token_text == ":":
            is_after_colon = True
        elif token_type not in pygments.token.Comment:
            is_whitespace = len(token_text.rstrip(" \f\n\r\t")) == 0
            if not is_whitespace:
                is_after_colon = False
        yield token_type, token_text


def _line_parts(lexer, text):
    line_marks = set()
    tokens = _delined_tokens(lexer.get_tokens(text))
    if lexer.name == "Python":
        tokens = _pythonized_comments(tokens)
    language_id = lexer.name.lower()
    white_text = " \f\n\r\t" + white_characters(language_id)
    white_words = white_code_words(language_id)
    for token_type, token_text in tokens:
        if token_type in pygments.token.Comment:
            line_marks.add("d")  # 'documentation'
        elif token_type in pygments.token.String:
            line_marks.add("s")  # 'string'
        else:
            is_white_text = (token_text.strip() in white_words) or (token_text.rstrip(white_text) == "")
            if not is_white_text:
                line_marks.add("c")  # 'code'
        if token_text.endswith("\n"):
            yield line_marks
            line_marks = set()
    if len(line_marks) >= 1:
        yield line_marks


def encoding_for(source_path, encoding="automatic", fallback_encoding=None):
    """
    The encoding used by the text file stored in ``source_path``.

    The algorithm used is:

    * If ``encoding`` is ``'automatic``, attempt the following:
      1. Check BOM for UTF-8, UTF-16 and UTF-32.
      2. Look for XML prolog or magic heading like ``# -*- coding: cp1252 -*-``
      3. Read the file using UTF-8.
      4. If all this fails, use assume the ``fallback_encoding``.
    * If ``encoding`` is ``'chardet`` use :mod:`chardet` to obtain the encoding.
    * For any other ``encoding`` simply use the specified value.
    """
    assert encoding is not None

    if encoding == "automatic":
        with open(source_path, "rb") as source_file:
            heading = source_file.read(128)
        result = None
        if len(heading) == 0:
            # File is empty, assume a dummy encoding.
            result = "utf-8"
        if result is None:
            # Check for known BOMs.
            for bom, encoding in _BOM_TO_ENCODING_MAP.items():
                if heading[: len(bom)] == bom:
                    result = encoding
                    break
        if result is None:
            # Look for common headings that indicate the encoding.
            ascii_heading = heading.decode("ascii", errors="replace")
            ascii_heading = ascii_heading.replace("\r\n", "\n")
            ascii_heading = ascii_heading.replace("\r", "\n")
            ascii_heading = "\n".join(ascii_heading.split("\n")[:2]) + "\n"
            coding_magic_match = _CODING_MAGIC_REGEX.match(ascii_heading)
            if coding_magic_match is not None:
                result = coding_magic_match.group("encoding")
            else:
                first_line = ascii_heading.split("\n")[0]
                xml_prolog_match = _XML_PROLOG_REGEX.match(first_line)
                if xml_prolog_match is not None:
                    result = xml_prolog_match.group("encoding")
    elif encoding == "chardet":
        assert (
            _detector is not None
        ), 'without chardet installed, encoding="chardet" must be rejected before calling encoding_for()'
        _detector.reset()
        with open(source_path, "rb") as source_file:
            for line in source_file.readlines():
                _detector.feed(line)
                if _detector.done:
                    break
        result = _detector.result["encoding"]
        if result is None:
            _log.warning(
                "%s: chardet cannot determine encoding, assuming fallback encoding %s", source_path, fallback_encoding
            )
            result = fallback_encoding
    else:
        # Simply use the specified encoding.
        result = encoding
    if result is None:
        # Encoding 'automatic' or 'chardet' failed to detect anything.
        if fallback_encoding is not None:
            # If defined, use the fallback encoding.
            result = fallback_encoding
        else:
            try:
                # Attempt to read the file as UTF-8.
                with open(source_path, "r", encoding="utf-8") as source_file:
                    source_file.read()
                result = "utf-8"
            except UnicodeDecodeError:
                # UTF-8 did not work out, use the default as last resort.
                result = DEFAULT_FALLBACK_ENCODING
            _log.debug("%s: no fallback encoding specified, using %s", source_path, result)

    assert result is not None
    return result


def pseudo_source_analysis(source_path, group, state, state_info=None):
    assert source_path is not None
    assert group is not None
    assert isinstance(state, SourceState)
    return SourceAnalysis(
        path=source_path,
        language="__" + state.name + "__",
        group=group,
        code=0,
        documentation=0,
        empty=0,
        string=0,
        state=state.name,
        state_info=state_info,
    )


#: BOMs to indicate that a file is a text file even if it contains zero bytes.
_TEXT_BOMS = (codecs.BOM_UTF16_BE, codecs.BOM_UTF16_LE, codecs.BOM_UTF32_BE, codecs.BOM_UTF32_LE, codecs.BOM_UTF8)


def is_binary_file(source_path):
    with open(source_path, "rb") as source_file:
        initial_bytes = source_file.read(8192)
    return not any(initial_bytes.startswith(bom) for bom in _TEXT_BOMS) and b"\0" in initial_bytes


def is_plain_text(source_path):
    return _PLAIN_TEXT_NAME_REGEX.match(os.path.basename(source_path))


def has_lexer(source_path):
    """
    Initial quick check if there is a lexer for ``source_path``. This removes
    the need for calling :py:func:`pygments.lexers.guess_lexer_for_filename()`
    which fully reads the source file.
    """
    result = bool(pygments.lexers.find_lexer_class_for_filename(source_path))
    if not result:
        suffix = os.path.splitext(os.path.basename(source_path))[1].lstrip(".")
        result = suffix in _SUFFIX_TO_FALLBACK_LEXER_MAP
    return result


def guess_lexer(source_path, text):
    if is_plain_text(source_path):
        result = pygount.lexers.PlainTextLexer()
    else:
        try:
            result = pygments.lexers.guess_lexer_for_filename(source_path, text)
        except pygments.util.ClassNotFound:
            suffix = os.path.splitext(os.path.basename(source_path))[1].lstrip(".")
            result = _SUFFIX_TO_FALLBACK_LEXER_MAP.get(suffix)
    return result


def source_analysis(
    source_path,
    group,
    encoding="automatic",
    fallback_encoding="cp1252",
    generated_regexes=pygount.common.regexes_from(DEFAULT_GENERATED_PATTERNS_TEXT),
    duplicate_pool=None,
):
    """
    Analysis for line counts in source code stored in ``source_path``.

    :param source_path:
    :param group: name of a logical group the sourc code belongs to, e.g. a
      package.
    :param encoding: encoding according to :func:`encoding_for`
    :param fallback_encoding: fallback encoding according to
      :func:`encoding_for`
    :return: a :class:`SourceAnalysis`
    """
    assert encoding is not None
    assert generated_regexes is not None

    result = None
    lexer = None
    source_code = None
    source_size = os.path.getsize(source_path)
    if source_size == 0:
        _log.info("%s: is empty", source_path)
        result = pseudo_source_analysis(source_path, group, SourceState.empty)
    elif is_binary_file(source_path):
        _log.info("%s: is binary", source_path)
        result = pseudo_source_analysis(source_path, group, SourceState.binary)
    elif not has_lexer(source_path):
        _log.info("%s: unknown language", source_path)
        result = pseudo_source_analysis(source_path, group, SourceState.unknown)
    elif duplicate_pool is not None:
        duplicate_path = duplicate_pool.duplicate_path(source_path)
        if duplicate_path is not None:
            _log.info("%s: is a duplicate of %s", source_path, duplicate_path)
            result = pseudo_source_analysis(source_path, group, SourceState.duplicate, duplicate_path)
    if result is None:
        if encoding in ("automatic", "chardet"):
            encoding = encoding_for(source_path, encoding, fallback_encoding)
        try:
            with open(source_path, "r", encoding=encoding) as source_file:
                source_code = source_file.read()
        except (LookupError, OSError, UnicodeError) as error:
            _log.warning("cannot read %s using encoding %s: %s", source_path, encoding, error)
            result = pseudo_source_analysis(source_path, group, SourceState.error, error)
        if result is None:
            lexer = guess_lexer(source_path, source_code)
            assert lexer is not None
    if (result is None) and (len(generated_regexes) != 0):
        number_line_and_regex = matching_number_line_and_regex(pygount.common.lines(source_code), generated_regexes)
        if number_line_and_regex is not None:
            number, _, regex = number_line_and_regex
            message = "line {0} matches {1}".format(number, regex)
            _log.info("%s: is generated code because %s", source_path, message)
            result = pseudo_source_analysis(source_path, group, SourceState.generated, message)
    if result is None:
        assert lexer is not None
        assert source_code is not None
        language = lexer.name
        if ("xml" in language.lower()) or (language == "Genshi"):
            dialect = pygount.xmldialect.xml_dialect(source_path, source_code)
            if dialect is not None:
                language = dialect
        _log.info("%s: analyze as %s using encoding %s", source_path, language, encoding)
        mark_to_count_map = {"c": 0, "d": 0, "e": 0, "s": 0}
        for line_parts in _line_parts(lexer, source_code):
            mark_to_increment = "e"
            for mark_to_check in ("d", "s", "c"):
                if mark_to_check in line_parts:
                    mark_to_increment = mark_to_check
            mark_to_count_map[mark_to_increment] += 1
        result = SourceAnalysis(
            path=source_path,
            language=language,
            group=group,
            code=mark_to_count_map["c"],
            documentation=mark_to_count_map["d"],
            empty=mark_to_count_map["e"],
            string=mark_to_count_map["s"],
            state=SourceState.analyzed.name,
            state_info=None,
        )

    assert result is not None
    return result


class DuplicatePool:
    def __init__(self):
        self._size_to_paths_map = {}
        self._size_and_hash_to_path_map = {}

    @staticmethod
    def _hash_for(path_to_hash):
        buffer_size = 1024 * 1024
        md5_hash = hashlib.md5()
        with open(path_to_hash, "rb", buffer_size) as file_to_hash:
            data = file_to_hash.read(buffer_size)
            while len(data) >= 1:
                md5_hash.update(data)
                data = file_to_hash.read(buffer_size)
        return md5_hash.digest()

    def duplicate_path(self, source_path):
        result = None
        source_size = os.path.getsize(source_path)
        paths_with_same_size = self._size_to_paths_map.get(source_size)
        if paths_with_same_size is None:
            self._size_to_paths_map[source_size] = [source_path]
        else:
            source_hash = DuplicatePool._hash_for(source_path)
            if len(paths_with_same_size) == 1:
                # Retrofit the initial path with the same size and its hash.
                initial_path_with_same_size = paths_with_same_size[0]
                initial_hash = DuplicatePool._hash_for(initial_path_with_same_size)
                self._size_and_hash_to_path_map[(source_size, initial_hash)] = initial_path_with_same_size
            result = self._size_and_hash_to_path_map.get((source_size, source_hash))
            self._size_and_hash_to_path_map[(source_size, source_hash)] = source_path
        return result
