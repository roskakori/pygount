"""
Functions to analyze source code and count lines in it.
"""
# Copyright (c) 2016-2022, Thomas Aglassinger.
# All rights reserved. Distributed under the BSD License.
import codecs
import collections
import glob
import hashlib
import itertools
import logging
import os
import re
from enum import Enum
from typing import Dict, Generator, List, Optional, Pattern, Sequence, Set, Tuple, Union

import pygments.lexer
import pygments.lexers
import pygments.token
import pygments.util

import pygount.common
import pygount.lexers
import pygount.xmldialect
from pygount.common import deprecated

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
    [".?*", "_svn", "__pycache__"]  # Subversion hack for Windows  # Python byte code
)


#: Pygments token type; we need to define our own type because pygments' ``_TokenType`` is internal.
TokenType = type(pygments.token.Token)


class SourceState(Enum):
    """
    Possible values for :py:attr:`SourceAnalysis.state`.
    """

    #: successfully analyzed
    analyzed = 1
    #: source code is a binary
    binary = 2
    #: source code is an identical copy of another
    duplicate = 3
    #: source code is empty (file size = 0)
    empty = 4
    #: source could not be parsed
    error = 5
    #: source code has been generated
    generated = 6
    # TODO: 'huge' = auto()  # source code exceeds size limit
    #: pygments does not offer any lexer to analyze the source
    unknown = 7


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

_STANDARD_PLAIN_TEXT_NAME_PATTERNS = (
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
    # Github community recommendations, see
    # <https://docs.github.com/en/communities/setting-up-your-project-for-healthy-contributions>.
    # By now, in practice most projects use a suffix like "*.md" but some older ones
    # still might have such files without suffix.
    "code_of_conduct",
    "contributing",
    "support",
    # Other common text files.
    "changes",
    "faq",
    "readme\\.1st",
    "read\\.me",
    "todo",
)
_PLAIN_TEXT_PATTERN = "(^" + "$)|(^".join(_STANDARD_PLAIN_TEXT_NAME_PATTERNS) + "$)"
#: Regular expression to detect plain text files by name.
_PLAIN_TEXT_NAME_REGEX = re.compile(_PLAIN_TEXT_PATTERN, re.IGNORECASE)


#: Mapping for file suffixes to lexers for which pygments offers no official one.
_SUFFIX_TO_FALLBACK_LEXER_MAP = {
    "fex": pygount.lexers.MinimalisticWebFocusLexer(),
    "idl": pygount.lexers.IdlLexer(),
    "m4": pygount.lexers.MinimalisticM4Lexer(),
    "txt": pygount.lexers.PlainTextLexer(),
    "vbe": pygount.lexers.MinimalisticVBScriptLexer(),
    "vbs": pygount.lexers.MinimalisticVBScriptLexer(),
}
for _oracle_suffix in ("pck", "pkb", "pks", "pls"):
    _SUFFIX_TO_FALLBACK_LEXER_MAP[_oracle_suffix] = pygments.lexers.get_lexer_by_name("plpgsql")


class DuplicatePool:
    """
    A pool that collects information about potential duplicate files.
    """

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

    def duplicate_path(self, source_path: str) -> Optional[str]:
        """
        Path to a duplicate for ``source_path`` or ``None`` if no duplicate exists.

        Internally information is stored to identify possible future duplicates of
        ``source_path``.
        """
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


class SourceAnalysis:
    """
    Results from analyzing a source path.

    Prefer the factory methods :py:meth:`from_file()` and :py:meth:`from_state` to
    calling the constructor.
    """

    def __init__(
        self,
        path: str,
        language: str,
        group: str,
        code: int,
        documentation: int,
        empty: int,
        string: int,
        state: SourceState,
        state_info: Optional[str] = None,
    ):
        SourceAnalysis._check_state_info(state, state_info)
        self._path = path
        self._language = language
        self._group = group
        self._code = code
        self._documentation = documentation
        self._empty = empty
        self._string = string
        self._state = state
        self._state_info = state_info

    @staticmethod
    def from_state(
        source_path: str, group: str, state: SourceState, state_info: Optional[str] = None
    ) -> "SourceAnalysis":
        """
        Factory method to create a :py:class:`SourceAnalysis` with all counts
        set to 0 and everything else according to the specified parameters.
        """
        assert source_path is not None
        assert group is not None
        assert state != SourceState.analyzed, "use from() for analyzable sources"
        SourceAnalysis._check_state_info(state, state_info)
        return SourceAnalysis(
            path=source_path,
            language=f"__{state.name}__",
            group=group,
            code=0,
            documentation=0,
            empty=0,
            string=0,
            state=state,
            state_info=state_info,
        )

    @staticmethod
    def _check_state_info(state: SourceState, state_info: Optional[str]):
        states_that_require_state_info = [SourceState.duplicate, SourceState.error, SourceState.generated]
        assert (state in states_that_require_state_info) == (
            state_info is not None
        ), "state={} and state_info={} but state_info must be specified for the following states: {}".format(
            state,
            state_info,
            states_that_require_state_info,
        )

    @staticmethod
    def from_file(
        source_path: str,
        group: str,
        encoding: str = "automatic",
        fallback_encoding: str = "cp1252",
        generated_regexes=pygount.common.regexes_from(DEFAULT_GENERATED_PATTERNS_TEXT),
        duplicate_pool: Optional[DuplicatePool] = None,
    ) -> "SourceAnalysis":
        """
        Factory method to create a :py:class:`SourceAnalysis` by analyzing
        the source code in ``source_path``.

        :param source_path: path to source code to analyze
        :param group: name of a logical group the sourc code belongs to, e.g. a
          package.
        :param encoding: encoding according to :func:`encoding_for`
        :param fallback_encoding: fallback encoding according to
          :func:`encoding_for`
        :param generated_regexes: list of regular expression that if found within the first few lines
          if a source code identify is as generated source code for which SLOC should not be counted
        :param duplicate_pool: a :class:`DuplicatePool` where information about possible duplicates is
          collected, or ``None`` if possible duplicates should be counted multiple times.
        """
        assert encoding is not None
        assert generated_regexes is not None

        result = None
        lexer = None
        source_code = None
        source_size = os.path.getsize(source_path)
        if source_size == 0:
            _log.info("%s: is empty", source_path)
            result = SourceAnalysis.from_state(source_path, group, SourceState.empty)
        elif is_binary_file(source_path):
            _log.info("%s: is binary", source_path)
            result = SourceAnalysis.from_state(source_path, group, SourceState.binary)
        elif not has_lexer(source_path):
            _log.info("%s: unknown language", source_path)
            result = SourceAnalysis.from_state(source_path, group, SourceState.unknown)
        elif duplicate_pool is not None:
            duplicate_path = duplicate_pool.duplicate_path(source_path)
            if duplicate_path is not None:
                _log.info("%s: is a duplicate of %s", source_path, duplicate_path)
                result = SourceAnalysis.from_state(source_path, group, SourceState.duplicate, duplicate_path)
        if result is None:
            if encoding in ("automatic", "chardet"):
                encoding = encoding_for(source_path, encoding, fallback_encoding)
            try:
                with open(source_path, encoding=encoding) as source_file:
                    source_code = source_file.read()
            except (LookupError, OSError, UnicodeError) as error:
                _log.warning("cannot read %s using encoding %s: %s", source_path, encoding, error)
                result = SourceAnalysis.from_state(source_path, group, SourceState.error, error)
            if result is None:
                lexer = guess_lexer(source_path, source_code)
                assert lexer is not None
        if (result is None) and (len(generated_regexes) != 0):
            number_line_and_regex = matching_number_line_and_regex(pygount.common.lines(source_code), generated_regexes)
            if number_line_and_regex is not None:
                number, _, regex = number_line_and_regex
                message = f"line {number} matches {regex}"
                _log.info("%s: is generated code because %s", source_path, message)
                result = SourceAnalysis.from_state(source_path, group, SourceState.generated, message)
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
                state=SourceState.analyzed,
                state_info=None,
            )

        assert result is not None
        return result

    @property
    def path(self) -> str:
        return self._path

    @property
    def language(self) -> str:
        """
        The programming language the analyzed source code is written in; if
        :py:attr:`state` does not equal :py:attr:`SourceState.analyzed` this
        will be a pseudo language.
        """
        return self._language

    @property
    def group(self) -> str:
        """
        Group the source code belongs to; this can be any text useful to group
        the files later on. It is perfectly valid to put all files in the same
        group.

        (Note: this property is mostly there for compatibility with the
        original SLOCCount.)
        """
        return self._group

    @property
    def code_count(self) -> int:
        """number of lines containing code"""
        return self._code

    @property
    def documentation_count(self) -> int:
        """number of lines containing documentation (resp. comments)"""
        return self._documentation

    @property
    def empty_count(self) -> int:
        """
        number of empty lines, including lines containing only white space,
        white characters or white code words

        See also: :py:func:`white_characters`, :py:func:`white_code_words`
        """
        return self._empty

    @property
    def string_count(self) -> int:
        """number of lines containing only strings but no other code"""
        return self._string

    @property
    def source_count(self) -> int:
        """number of source lines of code (the sum of code_count and string_count)"""
        return self.code_count + self.string_count

    @property
    def code(self) -> int:
        # TODO #47: Remove deprecated property.
        return self._code

    @property
    def documentation(self) -> int:
        # TODO #47: Remove deprecated property.
        return self._documentation

    @property
    def empty(self) -> int:
        # TODO #47: Remove deprecated property.
        return self._empty

    @property
    def string(self) -> int:
        # TODO #47: Remove deprecated property.
        return self._string

    @property
    def state(self) -> SourceState:
        """
        The state of the analysis after parsing the source file.
        """
        return self._state

    @property
    def state_info(self) -> Optional[Union[str, Exception]]:
        """
        Possible additional information about :py:attr:`state`:

        * :py:attr:`SourceState.duplicate`: path to the original source file
          the :py:attr:`path` is a duplicate of
        * :py:attr:`SourceState.error`: the :py:exc:`Exception` causing the
          error
        * :py:attr:`SourceState.generated`: a human readable explanation why
          the file is considered to be generated
        """
        return self._state_info

    @property
    def is_countable(self) -> bool:
        """
        ``True`` if source counts can be counted towards a total.
        """
        return self.state in (SourceState.analyzed, SourceState.duplicate)

    def __repr__(self):
        result = "{}(path={!r}, language={!r}, group={!r}, state={}".format(
            self.__class__.__name__, self.path, self.language, self.group, self.state.name
        )
        if self.state == SourceState.analyzed:
            result += ", code_count={}, documentation_count={}, empty_count={}, string_count={}".format(
                self.code_count, self.documentation_count, self.empty_count, self.string_count
            )
        if self.state_info is not None:
            result += f", state_info={self.state_info!r}"
        result += ")"
        return result


class SourceScanner:
    """
    Scanner for source code files matching certain conditions.
    """

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
    def folder_regexps_to_skip(self, regexps_or_pattern_text):
        self._folder_regexps_to_skip.append = pygount.common.regexes_from(
            regexps_or_pattern_text, self.folder_regexps_to_skip
        )

    @property
    def name_regexps_to_skip(self):
        return self._name_regexps_to_skip

    @name_regexps_to_skip.setter
    def name_regexps_to_skip(self, regexps_or_pattern_text):
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
                raise OSError(f'cannot scan "{pattern}" for source files: {error}')
        result = sorted(set(result))
        return result

    def source_paths(self) -> Generator[str, None, None]:
        """
        Paths to source code files matching all the conditions for this scanner.
        """
        source_paths_and_groups_to_analyze = self._source_paths_and_groups_to_analyze(self.source_patterns)

        for source_path, group in source_paths_and_groups_to_analyze:
            suffix = os.path.splitext(source_path)[1].lstrip(".")
            is_suffix_to_analyze = any(suffix_regexp.match(suffix) for suffix_regexp in self.suffixes)
            if is_suffix_to_analyze:
                yield source_path, group
            else:
                _log.info("skip due to suffix: %s", source_path)


_LANGUAGE_TO_WHITE_WORDS_MAP = {"batchfile": {"@"}, "python": {"pass"}, "sql": {"begin", "end"}}
for _language in _LANGUAGE_TO_WHITE_WORDS_MAP.keys():
    assert _language.islower()


def matching_number_line_and_regex(
    source_lines: Sequence[str], generated_regexes: Sequence[Pattern], max_line_count: int = 15
) -> Optional[Tuple[int, str, Pattern]]:
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
    result = (
        possible_first_matching_number_line_and_regexp[0] if possible_first_matching_number_line_and_regexp else None
    )
    return result


def white_characters(language_id: str) -> str:
    """
    Characters that count as white space if they are the only characters in a
    line.
    """
    assert language_id is not None
    assert language_id.islower()
    return "(),:;[]{}"


def white_code_words(language_id: str) -> Dict[str, List[str]]:
    """
    Words that do not count as code if it is the only word in a line.
    """
    assert language_id is not None
    assert language_id.islower()
    return _LANGUAGE_TO_WHITE_WORDS_MAP.get(language_id, set())


def _delined_tokens(tokens: Sequence[Tuple[TokenType, str]]) -> Generator[TokenType, None, None]:
    for token_type, token_text in tokens:
        newline_index = token_text.find("\n")
        while newline_index != -1:
            yield token_type, token_text[: newline_index + 1]
            token_text = token_text[newline_index + 1 :]
            newline_index = token_text.find("\n")
        if token_text != "":
            yield token_type, token_text


def _pythonized_comments(tokens: Sequence[Tuple[TokenType, str]]) -> Generator[TokenType, None, None]:
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


def _line_parts(lexer: pygments.lexer.Lexer, text: str) -> Generator[Set[str], None, None]:
    line_marks = set()
    tokens = _delined_tokens(lexer.get_tokens(text))
    if lexer.name == "Python":
        tokens = _pythonized_comments(tokens)
    language_id = lexer.name.lower()
    white_text = " \f\n\r\t" + white_characters(language_id)
    white_words = white_code_words(language_id)
    for token_type, token_text in tokens:
        # NOTE: Pygments treats preprocessor statements as special comments.
        is_actual_comment = token_type in pygments.token.Comment and token_type not in (
            pygments.token.Comment.Preproc,
            pygments.token.Comment.PreprocFile,
        )
        if is_actual_comment:
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


def encoding_for(source_path: str, encoding: str = "automatic", fallback_encoding: Optional[str] = None) -> str:
    """
    The encoding used by the text file stored in ``source_path``.

    The algorithm used is:

    * If ``encoding`` is ``'automatic``, attempt the following:

      1. Check BOM for UTF-8, UTF-16 and UTF-32.
      2. Look for XML prolog or magic heading like ``# -*- coding: cp1252 -*-``
      3. Read the file using UTF-8.
      4. If all this fails, use the ``fallback_encoding`` and ignore any
         further encoding errors.

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
                with open(source_path, encoding="utf-8") as source_file:
                    source_file.read()
                result = "utf-8"
            except UnicodeDecodeError:
                # UTF-8 did not work out, use the default as last resort.
                result = DEFAULT_FALLBACK_ENCODING
            _log.debug("%s: no fallback encoding specified, using %s", source_path, result)

    assert result is not None
    return result


@deprecated(f"use {SourceAnalysis.__name__}.{SourceAnalysis.from_state.__name__}")
def pseudo_source_analysis(source_path, group, state, state_info=None):
    return SourceAnalysis.from_state(source_path, group, state, state_info)


#: BOMs to indicate that a file is a text file even if it contains zero bytes.
_TEXT_BOMS = (codecs.BOM_UTF16_BE, codecs.BOM_UTF16_LE, codecs.BOM_UTF32_BE, codecs.BOM_UTF32_LE, codecs.BOM_UTF8)


def is_binary_file(source_path: str) -> bool:
    with open(source_path, "rb") as source_file:
        initial_bytes = source_file.read(8192)
    return not any(initial_bytes.startswith(bom) for bom in _TEXT_BOMS) and b"\0" in initial_bytes


def is_plain_text(source_path):
    return _PLAIN_TEXT_NAME_REGEX.match(os.path.basename(source_path))


def has_lexer(source_path: str) -> bool:
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


def guess_lexer(source_path: str, text: str) -> pygments.lexer.Lexer:
    if is_plain_text(source_path):
        result = pygount.lexers.PlainTextLexer()
    else:
        try:
            result = pygments.lexers.guess_lexer_for_filename(source_path, text)
        except pygments.util.ClassNotFound:
            suffix = os.path.splitext(os.path.basename(source_path))[1].lstrip(".")
            result = _SUFFIX_TO_FALLBACK_LEXER_MAP.get(suffix)
    return result


@deprecated(f"use {SourceAnalysis.__name__}.{SourceAnalysis.from_file.__name__}")
def source_analysis(
    source_path,
    group,
    encoding="automatic",
    fallback_encoding="cp1252",
    generated_regexes=pygount.common.regexes_from(DEFAULT_GENERATED_PATTERNS_TEXT),
    duplicate_pool: Optional[DuplicatePool] = None,
):
    return SourceAnalysis.from_file(source_path, group, encoding, fallback_encoding, generated_regexes, duplicate_pool)
