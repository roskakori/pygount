"""
Command line interface for pygount.
"""
# Copyright (c) 2016, Thomas Aglassinger.
# All rights reserved. Distributed under the BSD License.
import argparse
import fnmatch
import logging
import os
import re
import sys

import pygount.analysis
import pygount.common
import pygount.write


#: Valid formats for option --format.
_VALID_FORMATS = ('cloc-xml', 'sloccount')

_DEFAULT_ENCODING = 'automatic;cp1252'
_DEFAULT_OUTPUT_FORMAT = 'sloccount'
_DEFAULT_OUTPUT = 'STDOUT'
_DEFAULT_SOURCE_PATTERNS = os.curdir
_DEFAULT_SUFFICES = '*'

_HELP_ENCODING = '''encoding to use when reading source code; use "automatic"
 to take BOMs, XML prolog and magic headers into account and fall back to
 UTF-8 or CP1252 if none fits; use "automatic;<fallback>" to specify a
 different fallback encoding than CP1252; use "chardet" to let the chardet
 package determine the encoding; default: "%(default)s"'''

_HELP_FORMAT = 'output format, one of: {0}; default: "%(default)s"'.format(
    ', '.join(['"' + format + '"' for format in _VALID_FORMATS]))

_HELP_FOLDERS_TO_SKIP = '''comma separated list of glob patterns for folder
 names not to analyze. Use "..." as first entry to append patterns to the
 default patterns; default: %(default)s'''

_HELP_NAMES_TO_SKIP = '''comma separated list of glob patterns for file names
 not to analyze. Use "..." as first entry to append patterns to the default
 patterns; default: %(default)s'''

_HELP_SUFFIX = '''limit analysis on files matching any suffix in comma
 separated LIST; shell patterns are possible; example: "py,sql"; default:
 "%(default)s"'''

_log = logging.getLogger('pygount')


def _as_list(items_or_text):
    if isinstance(items_or_text, str):
        result = [item.strip() for item in items_or_text.split(',')]
    else:
        result = list(items_or_text)
    return result


def _glob_patterns(patterns, default_patterns):
    if isinstance(patterns, str):
        result = []
        for pattern in _as_list(patterns):
            if pattern == '...':
                result.extend(default_patterns)
            else:
                result.append(pattern)
    else:
        result = patterns
    return result


def _regexs_from(patterns_or_text):
    if isinstance(patterns_or_text, str):
        patterns = [pattern.strip() for pattern in patterns_or_text.split(',')]
    else:
        patterns = patterns_or_text
    return [re.compile(fnmatch.translate(pattern)) for pattern in patterns]


def _check_encoding(name, encoding_to_check, alternative_encoding, source=None):
    """
    Check that ``encoding`` is a valid Python encoding
    :param name: name under which the encoding is known to the user, e.g. 'default encoding'
    :param encoding_to_check: name of the encoding to check, e.g. 'utf-8'
    :param source: source where the encoding has been set, e.g. option name
    :raise pygount.common.OptionError if ``encoding`` is not a valid Python encoding
    """
    if encoding_to_check != alternative_encoding:
        try:
            ''.encode(encoding_to_check)
        except LookupError:
            raise pygount.common.OptionError(
                '{0} is "{1}" but must be "{2}" or a known Python encoding'.format(
                    name, encoding_to_check, alternative_encoding),
                source)


class Command():
    """
    Command interface for pygount, where options starting with defaults can
    gradually be set and finally :py:meth:`execute()`.
    """
    def __init__(self):
        self._default_encoding, self._fallback_encoding = _DEFAULT_ENCODING.split(';')
        self._folders_to_skip = _regexs_from(pygount.analysis.DEFAULT_FOLDER_GLOB_PATTERNS_TO_SKIP)
        self._is_verbose = False
        self._names_to_skip = _regexs_from(pygount.analysis.DEFAULT_NAME_GLOB_PATTERNS_TO_SKIP)
        self._output = _DEFAULT_OUTPUT
        self._output_format = _DEFAULT_OUTPUT_FORMAT
        self._source_patterns = _regexs_from(_DEFAULT_SOURCE_PATTERNS)
        self._suffices = _as_list(_DEFAULT_SUFFICES)

    def set_encodings(self, encoding, source=None):
        if encoding == 'automatic':
            default_encoding = encoding
            fallback_encoding = 'cp1252'
        elif encoding == 'chardet':
            if not pygount.analysis.has_chardet:  # pragma: no cover
                raise pygount.common.OptionError(
                    'chardet must be installed to set default encoding to "chardet"')
            default_encoding = encoding
            fallback_encoding = None
        else:
            if encoding.startswith('automatic;'):
                first_encoding_semicolon_index = encoding.find(';')
                default_encoding = encoding[:first_encoding_semicolon_index]
                fallback_encoding = encoding[first_encoding_semicolon_index + 1:]
                encoding_to_check = ('fallback encoding', fallback_encoding)
            else:
                default_encoding = encoding
                fallback_encoding = None
                encoding_to_check = ('encoding', default_encoding)
            if encoding_to_check is not None:
                name, encoding = encoding_to_check
                try:
                    ''.encode(encoding)
                except LookupError:
                    raise pygount.common.OptionError(
                        '{0} is "{1}" but must be a known Python encoding'.format(name, encoding))
        self.set_default_encoding(default_encoding, source)
        self.set_fallback_encoding(fallback_encoding, source)

    @property
    def default_encoding(self):
        return self._default_encoding

    def set_default_encoding(self, default_encoding, source=None):
        _check_encoding('default encoding', default_encoding, 'automatic', source)
        self._default_encoding = default_encoding

    @property
    def fallback_encoding(self):
        return self._fallback_encoding

    def set_fallback_encoding(self, fallback_encoding, source=None):
        _check_encoding('fallback encoding', fallback_encoding, 'automatic', source)
        self._fallback_encoding = fallback_encoding

    @property
    def folders_to_skip(self):
        return self._folders_to_skip

    def append_folder_to_skip(self, folder_glob_pattern_to_skip, source=None):
        self._folders_to_skip.extend(
            _regexs_from(_glob_patterns([folder_glob_pattern_to_skip])))

    def clear_folder_to_skip(self, source=None):
        self._folders_to_skip = []

    def set_folders_to_skip(self, folder_glob_patterns_to_skip, source=None):
        self._folders_to_skip = _regexs_from(
            _glob_patterns(folder_glob_patterns_to_skip, pygount.analysis.DEFAULT_FOLDER_GLOB_PATTERNS_TO_SKIP))

    @property
    def is_verbose(self):
        self._is_verbose

    def set_is_verbose(self, is_verbose, source=None):
        self._is_verbose = bool(is_verbose)

    @property
    def names_to_skip(self):
        return self._names_to_skip

    def append_name_to_skip(self, name_glob_pattern_to_skip, source=None):
        self._names_to_skip.extend(
            _regexs_from(_glob_patterns([name_glob_pattern_to_skip])))

    def clear_names_to_skip(self, source=None):
        self._names_to_skip = []

    def set_names_to_skip(self, name_glob_patterns_to_skip, source=None):
        self._names_to_skip = _regexs_from(
            _glob_patterns(name_glob_patterns_to_skip, pygount.analysis.DEFAULT_NAME_GLOB_PATTERNS_TO_SKIP))

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
        if output_format not in _VALID_FORMATS:
            raise pygount.common.OptionError(
                'format is {0} but must be one of: {1}'.format(output_format, _VALID_FORMATS),
                source)
        self._output_format = output_format

    @property
    def source_patterns(self):
        return self._source_patterns

    def set_source_patterns(self, source_patterns, source=None):
        self._source_patterns = _glob_patterns(source_patterns, _DEFAULT_SOURCE_PATTERNS)

    @property
    def suffices(self):
        return self._suffices

    def set_suffices(self, suffices, source=None):
        assert suffices is not None
        self._suffices = _as_list(suffices)

    def argument_parser(self):
        parser = argparse.ArgumentParser(description='count source lines of code')
        parser.add_argument(
            '--encoding', '-e', default=_DEFAULT_ENCODING, help=_HELP_ENCODING
        )
        parser.add_argument(
            '--folders-to-skip', '-F', metavar='GLOBPATTERNS',
            default=', '.join(pygount.analysis.DEFAULT_FOLDER_GLOB_PATTERNS_TO_SKIP),
            help=_HELP_FOLDERS_TO_SKIP
        )
        parser.add_argument(
            '--format', '-f', metavar='FORMAT', choices=_VALID_FORMATS,
            default=_DEFAULT_OUTPUT_FORMAT,
            help=_HELP_FORMAT
        )
        parser.add_argument(
            '--names-to-skip', '-N', metavar='GLOBPATTERNS',
            default=', '.join(pygount.analysis.DEFAULT_NAME_GLOB_PATTERNS_TO_SKIP),
            help=_HELP_NAMES_TO_SKIP
        )
        parser.add_argument(
            '--out', '-o', metavar='FILE', default=_DEFAULT_OUTPUT,
            help='file to write results to; use "STDOUT" for standard output; default: "%(default)s"'
        )
        parser.add_argument(
            '--suffix', '-s', metavar='LIST', default='*', help=_HELP_SUFFIX
        )
        parser.add_argument(
            'source_patterns', metavar='PATTERN', nargs='*', default=[os.getcwd()],
            help='source files and directories to scan; can use glob patterns; default: current directory')
        parser.add_argument('--verbose', '-v', action='store_true', help='explain what is being done')
        parser.add_argument('--version', action='version', version='%(prog)s ' + pygount.common.__version__)
        return parser

    def parsed_args(self, arguments):
        assert arguments is not None

        parser = self.argument_parser()
        args = parser.parse_args(arguments)
        if args.encoding == 'automatic':
            default_encoding = args.encoding
            fallback_encoding = 'cp1252'
        elif args.encoding == 'chardet':
            if not pygount.analysis.has_chardet:  # pragma: no cover
                parser.error('chardet must be installed in order to specify --encoding=chardet')
            default_encoding = args.encoding
            fallback_encoding = None
        else:
            if args.encoding.startswith('automatic;'):
                first_encoding_semicolon_index = args.encoding.find(';')
                default_encoding = args.encoding[:first_encoding_semicolon_index]
                fallback_encoding = args.encoding[first_encoding_semicolon_index + 1:]
                encoding_to_check = ('fallback encoding', fallback_encoding)
            else:
                default_encoding = args.encoding
                fallback_encoding = None
                encoding_to_check = ('encoding', default_encoding)
            if encoding_to_check is not None:
                name, encoding = encoding_to_check
                try:
                    ''.encode(encoding)
                except LookupError:
                    parser.error('{0} specified with --encoding must be a known Python encoding: {1}'.format(
                        name, encoding))
        return args, default_encoding, fallback_encoding

    def apply_arguments(self, arguments=None):
        if arguments is None:  # pragma: no cover
            arguments = sys.argv[1:]
        args, default_encoding, fallback_encoding = self.parsed_args(arguments)
        self.set_default_encoding(default_encoding, 'option --encoding')
        self.set_fallback_encoding(fallback_encoding, 'option --encoding')
        self.set_folders_to_skip(args.folders_to_skip, 'option --folders-to-skip')
        self.set_is_verbose(args.verbose, 'option --verbose')
        self.set_names_to_skip(args.names_to_skip, 'option --folders-to-skip')
        self.set_output(args.out, 'option --out')
        self.set_output_format(args.format, 'option --format')
        self.set_source_patterns(args.source_patterns, 'option PATTERNS')
        self.set_suffices(args.suffix, 'option --suffix')

    def execute(self):
        source_scanner = pygount.analysis.SourceScanner(
            self.source_patterns,
            self.suffices)
        source_paths_and_groups_to_analyze = source_scanner.source_paths()

        if self.output == 'STDOUT':
            target_file = sys.stdout
            has_target_file_to_close = False
        else:
            target_file = open(self.output, 'w', encoding='utf-8', newline='')
            has_target_file_to_close = True

        try:
            if self.output_format == 'cloc-xml':
                writer_class = pygount.write.ClocXmlWriter
            else:
                assert self.output_format == 'sloccount'
                writer_class = pygount.write.LineWriter
            with writer_class(target_file) as writer:
                for source_path, group in source_paths_and_groups_to_analyze:
                    statistics = pygount.analysis.source_analysis(
                        source_path, group, self.default_encoding, self.fallback_encoding)
                    if statistics is not None:
                        if statistics.language is not None:
                            writer.add(statistics)
                        else:
                            _log.info('skip due unknown language: %s', statistics.path)
        finally:
            if has_target_file_to_close:
                try:
                    target_file.close()
                except Exception as error:
                    raise OSError(
                        'cannot write output to "{0}": {1}'.format(self.output, error))


def pygount_command(arguments=None):
    result = 1
    command = Command()
    try:
        command.apply_arguments(arguments)
        command.execute()
        result = 0
    except KeyboardInterrupt:  # pragma: no cover
        _log.error('interrupted as requested by user')
    except (pygount.common.OptionError, OSError) as error:
        _log.error(error)
    except Exception as error:
        _log.exception(error)

    return result


def main():  # pragma: no cover
    logging.basicConfig(level=logging.WARNING)
    sys.exit(pygount_command())


if __name__ == '__main__':  # pragma: no cover
    main()
