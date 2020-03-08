"""
Command line interface for pygount.
"""
# Copyright (c) 2016-2020, Thomas Aglassinger.
# All rights reserved. Distributed under the BSD License.
import argparse
import logging
import os
import sys

import pygount.analysis
import pygount.common
import pygount.write


#: Valid formats for option --format.
VALID_OUTPUT_FORMATS = ("cloc-xml", "sloccount", "summary")

_DEFAULT_ENCODING = "automatic"
_DEFAULT_OUTPUT_FORMAT = "sloccount"
_DEFAULT_OUTPUT = "STDOUT"
_DEFAULT_SOURCE_PATTERNS = os.curdir
_DEFAULT_SUFFIXES = "*"

_HELP_ENCODING = '''encoding to use when reading source code; use "automatic"
 to take BOMs, XML prolog and magic headers into account and fall back to
 UTF-8 or CP1252 if none fits; use "automatic;<fallback>" to specify a
 different fallback encoding than CP1252; use "chardet" to let the chardet
 package determine the encoding; default: "%(default)s"'''

_HELP_EPILOG = """SHELL-PATTERN is a pattern using *, ? and ranges like [a-z]
 as placeholders. PATTERNS is a comma separated list of SHELL-PATTERN. The
 prefix [regex] indicated that the PATTERNS use regular expression syntax. If
 default values are available, [...] indicates that the PATTERNS extend the
 existing default values."""

_HELP_FORMAT = 'output format, one of: {0}; default: "%(default)s"'.format(
    ", ".join(['"' + format + '"' for format in VALID_OUTPUT_FORMATS])
)

_HELP_GENERATED = """comma separated list of regular expressions to detect
 generated code; default: %(default)s"""

_HELP_FOLDERS_TO_SKIP = """comma separated list of glob patterns for folder
 names not to analyze. Use "..." as first entry to append patterns to the
 default patterns; default: %(default)s"""

_HELP_NAMES_TO_SKIP = """comma separated list of glob patterns for file names
 not to analyze. Use "..." as first entry to append patterns to the default
 patterns; default: %(default)s"""

_HELP_SUFFIX = '''limit analysis on files matching any suffix in comma
 separated LIST; shell patterns are possible; example: "py,sql"; default:
 "%(default)s"'''

_OUTPUT_FORMAT_TO_WRITER_CLASS_MAP = {
    "cloc-xml": pygount.write.ClocXmlWriter,
    "sloccount": pygount.write.LineWriter,
    "summary": pygount.write.SummaryWriter,
}
assert set(VALID_OUTPUT_FORMATS) == set(_OUTPUT_FORMAT_TO_WRITER_CLASS_MAP.keys())

_log = logging.getLogger("pygount")


def _check_encoding(name, encoding_to_check, alternative_encoding, source=None):
    """
    Check that ``encoding`` is a valid Python encoding
    :param name: name under which the encoding is known to the user, e.g. 'default encoding'
    :param encoding_to_check: name of the encoding to check, e.g. 'utf-8'
    :param source: source where the encoding has been set, e.g. option name
    :raise pygount.common.OptionError if ``encoding`` is not a valid Python encoding
    """
    assert name is not None

    if encoding_to_check not in (alternative_encoding, "chardet", None):
        try:
            "".encode(encoding_to_check)
        except LookupError:
            raise pygount.common.OptionError(
                '{0} is "{1}" but must be "{2}" or a known Python encoding'.format(
                    name, encoding_to_check, alternative_encoding
                ),
                source,
            )


class Command:
    """
    Command interface for pygount, where options starting with defaults can
    gradually be set and finally :py:meth:`execute()`.
    """

    def __init__(self):
        self.set_encodings(_DEFAULT_ENCODING)
        self._folders_to_skip = pygount.common.regexes_from(pygount.analysis.DEFAULT_FOLDER_PATTERNS_TO_SKIP_TEXT)
        self._generated_regexs = pygount.common.regexes_from(pygount.analysis.DEFAULT_GENERATED_PATTERNS_TEXT)
        self._has_duplicates = False
        self._has_summary = False
        self._is_verbose = False
        self._names_to_skip = pygount.common.regexes_from(pygount.analysis.DEFAULT_NAME_PATTERNS_TO_SKIP_TEXT)
        self._output = _DEFAULT_OUTPUT
        self._output_format = _DEFAULT_OUTPUT_FORMAT
        self._source_patterns = _DEFAULT_SOURCE_PATTERNS
        self._suffixes = pygount.common.regexes_from(_DEFAULT_SUFFIXES)

    def set_encodings(self, encoding, source=None):
        encoding_is_chardet = (encoding == "chardet") or (encoding.startswith("chardet;"))
        if encoding_is_chardet and not pygount.analysis.has_chardet:  # pragma: no cover
            raise pygount.common.OptionError('chardet must be installed to set default encoding to "chardet"')
        if encoding in ("automatic", "chardet"):
            default_encoding = encoding
            fallback_encoding = None
        else:
            if encoding.startswith("automatic;") or encoding.startswith("chardet;"):
                first_encoding_semicolon_index = encoding.find(";")
                default_encoding = encoding[:first_encoding_semicolon_index]
                fallback_encoding = encoding[first_encoding_semicolon_index + 1 :]
            else:
                default_encoding = encoding
                fallback_encoding = pygount.analysis.DEFAULT_FALLBACK_ENCODING
        self.set_default_encoding(default_encoding, source)
        self.set_fallback_encoding(fallback_encoding, source)

    @property
    def default_encoding(self):
        return self._default_encoding

    def set_default_encoding(self, default_encoding, source=None):
        _check_encoding("default encoding", default_encoding, "automatic", source)
        self._default_encoding = default_encoding

    @property
    def fallback_encoding(self):
        return self._fallback_encoding

    def set_fallback_encoding(self, fallback_encoding, source=None):
        _check_encoding("fallback encoding", fallback_encoding, "automatic", source)
        self._fallback_encoding = fallback_encoding

    @property
    def folders_to_skip(self):
        return self._folders_to_skip

    def set_folders_to_skip(self, regexes_or_patterns_text, source=None):
        self._folders_to_skip = pygount.common.regexes_from(
            regexes_or_patterns_text, pygount.analysis.DEFAULT_FOLDER_PATTERNS_TO_SKIP_TEXT, source
        )

    @property
    def generated_regexps(self):
        return self._generated_regexs

    def set_generated_regexps(self, regexes_or_patterns_text, source=None):
        self._generated_regexs = pygount.common.regexes_from(
            regexes_or_patterns_text, pygount.analysis.DEFAULT_GENERATED_PATTERNS_TEXT, source
        )

    @property
    def has_duplicates(self):
        return self._has_duplicates

    def set_has_duplicates(self, has_duplicates, source=None):
        self._has_duplicates = bool(has_duplicates)

    @property
    def is_verbose(self):
        return self._is_verbose

    def set_is_verbose(self, is_verbose, source=None):
        self._is_verbose = bool(is_verbose)

    @property
    def names_to_skip(self):
        return self._names_to_skip

    def set_names_to_skip(self, regexes_or_pattern_text, source=None):
        self._names_to_skip = pygount.common.regexes_from(
            regexes_or_pattern_text, pygount.analysis.DEFAULT_NAME_PATTERNS_TO_SKIP_TEXT, source
        )

    @property
    def output(self):
        return self._output

    def set_output(self, output, source=None):
        assert output is not None
        self._output = output

    @property
    def output_format(self):
        return self._output_format

    def set_output_format(self, output_format, source=None):
        assert output_format is not None
        if output_format not in VALID_OUTPUT_FORMATS:
            raise pygount.common.OptionError(
                "format is {0} but must be one of: {1}".format(output_format, VALID_OUTPUT_FORMATS), source
            )
        self._output_format = output_format

    @property
    def source_patterns(self):
        return self._source_patterns

    def set_source_patterns(self, glob_patterns_or_text, source=None):
        assert glob_patterns_or_text is not None
        self._source_patterns = pygount.common.as_list(glob_patterns_or_text)
        assert len(self._source_patterns) >= 0

    @property
    def suffixes(self):
        return self._suffixes

    def set_suffixes(self, regexes_or_patterns_text, source=None):
        assert regexes_or_patterns_text is not None
        self._suffixes = pygount.common.regexes_from(regexes_or_patterns_text, _DEFAULT_SUFFIXES, source)

    def argument_parser(self):
        parser = argparse.ArgumentParser(description="count source lines of code", epilog=_HELP_EPILOG)
        parser.add_argument("--duplicates", "-d", action="store_true", help="analyze duplicate files")
        parser.add_argument("--encoding", "-e", default=_DEFAULT_ENCODING, help=_HELP_ENCODING)
        parser.add_argument(
            "--folders-to-skip",
            "-F",
            metavar="PATTERNS",
            default=pygount.analysis.DEFAULT_FOLDER_PATTERNS_TO_SKIP_TEXT,
            help=_HELP_FOLDERS_TO_SKIP,
        )
        parser.add_argument(
            "--format",
            "-f",
            metavar="FORMAT",
            choices=VALID_OUTPUT_FORMATS,
            default=_DEFAULT_OUTPUT_FORMAT,
            help=_HELP_FORMAT,
        )
        parser.add_argument(
            "--generated",
            "-g",
            metavar="PATTERNS",
            default=pygount.analysis.DEFAULT_GENERATED_PATTERNS_TEXT,
            help=_HELP_GENERATED,
        )
        parser.add_argument(
            "--names-to-skip",
            "-N",
            metavar="PATTERNS",
            default=pygount.analysis.DEFAULT_NAME_PATTERNS_TO_SKIP_TEXT,
            help=_HELP_NAMES_TO_SKIP,
        )
        parser.add_argument(
            "--out",
            "-o",
            metavar="FILE",
            default=_DEFAULT_OUTPUT,
            help='file to write results to; use "STDOUT" for standard output; default: "%(default)s"',
        )
        parser.add_argument("--suffix", "-s", metavar="PATTERNS", default=_DEFAULT_SUFFIXES, help=_HELP_SUFFIX)
        parser.add_argument(
            "source_patterns",
            metavar="SHELL-PATTERN",
            nargs="*",
            default=[os.getcwd()],
            help="source files and directories to scan; can use glob patterns; default: current directory",
        )
        parser.add_argument("--verbose", "-v", action="store_true", help="explain what is being done")
        parser.add_argument("--version", action="version", version="%(prog)s " + pygount.common.__version__)
        return parser

    def parsed_args(self, arguments):
        assert arguments is not None

        parser = self.argument_parser()
        args = parser.parse_args(arguments)
        if args.encoding == "automatic":
            default_encoding = args.encoding
            fallback_encoding = None
        elif args.encoding == "chardet":
            if not pygount.analysis.has_chardet:  # pragma: no cover
                parser.error("chardet must be installed in order to specify --encoding=chardet")
            default_encoding = args.encoding
            fallback_encoding = None
        else:
            if args.encoding.startswith("automatic;"):
                first_encoding_semicolon_index = args.encoding.find(";")
                default_encoding = args.encoding[:first_encoding_semicolon_index]
                fallback_encoding = args.encoding[first_encoding_semicolon_index + 1 :]
                encoding_to_check = ("fallback encoding", fallback_encoding)
            else:
                default_encoding = args.encoding
                fallback_encoding = None
                encoding_to_check = ("encoding", default_encoding)
            if encoding_to_check is not None:
                name, encoding = encoding_to_check
                try:
                    "".encode(encoding)
                except LookupError:
                    parser.error(
                        "{0} specified with --encoding must be a known Python encoding: {1}".format(name, encoding)
                    )
        return args, default_encoding, fallback_encoding

    def apply_arguments(self, arguments=None):
        if arguments is None:  # pragma: no cover
            arguments = sys.argv[1:]
        args, default_encoding, fallback_encoding = self.parsed_args(arguments)
        self.set_default_encoding(default_encoding, "option --encoding")
        self.set_fallback_encoding(fallback_encoding, "option --encoding")
        self.set_folders_to_skip(args.folders_to_skip, "option --folders-to-skip")
        self.set_generated_regexps(args.generated, "option --generated")
        self.set_has_duplicates(args.duplicates, "option --duplicates")
        self.set_is_verbose(args.verbose, "option --verbose")
        self.set_names_to_skip(args.names_to_skip, "option --folders-to-skip")
        self.set_output(args.out, "option --out")
        self.set_output_format(args.format, "option --format")
        self.set_source_patterns(args.source_patterns, "option PATTERNS")
        self.set_suffixes(args.suffix, "option --suffix")

    def execute(self):
        _log.setLevel(logging.INFO if self.is_verbose else logging.WARNING)
        source_scanner = pygount.analysis.SourceScanner(
            self.source_patterns, self.suffixes, self.folders_to_skip, self.names_to_skip
        )
        source_paths_and_groups_to_analyze = list(source_scanner.source_paths())
        duplicate_pool = pygount.analysis.DuplicatePool() if not self.has_duplicates else None
        if self.output == "STDOUT":
            target_file = sys.stdout
            has_target_file_to_close = False
        else:
            target_file = open(self.output, "w", encoding="utf-8", newline="")
            has_target_file_to_close = True

        try:
            writer_class = _OUTPUT_FORMAT_TO_WRITER_CLASS_MAP[self.output_format]
            with writer_class(target_file) as writer:
                for source_path, group in source_paths_and_groups_to_analyze:
                    statistics = pygount.analysis.source_analysis(
                        source_path,
                        group,
                        self.default_encoding,
                        self.fallback_encoding,
                        generated_regexes=self._generated_regexs,
                        duplicate_pool=duplicate_pool,
                    )
                    writer.add(statistics)
        finally:
            if has_target_file_to_close:
                try:
                    target_file.close()
                except Exception as error:
                    raise OSError('cannot write output to "{0}": {1}'.format(self.output, error))


def pygount_command(arguments=None):
    result = 1
    command = Command()
    try:
        command.apply_arguments(arguments)
        command.execute()
        result = 0
    except KeyboardInterrupt:  # pragma: no cover
        _log.error("interrupted as requested by user")
    except (pygount.common.OptionError, OSError) as error:
        _log.error(error)
    except Exception as error:
        _log.exception(error)

    return result


def main():  # pragma: no cover
    logging.basicConfig(level=logging.WARNING)
    sys.exit(pygount_command())


if __name__ == "__main__":  # pragma: no cover
    main()
