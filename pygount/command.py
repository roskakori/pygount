"""
Command line inteface for pygount.
"""
# Copyright (c) 2016, Thomas Aglassinger.
# All rights reserved. Distributed under the BSD License.
import argparse
import fnmatch
import glob
import logging
import os
import re
import sys

import pygount
import pygount.analysis
import pygount.write

#: Valid formats for option --format.
_VALID_FORMATS = ('cloc-xml', 'sloccount')

_HELP_ENCODING = '''encoding to use when reading source code; use "automatic"
 to take BOMs, XML prolog and magic headers into account and fall back to
 UTF-8 or CP1252 if none fits; use "automatic;<fallback>" to specify a
 different fallback encoding than CP1252; use "chardet" to let the chardet
 package determine the encoding; default: "%(default)s"'''

_HELP_FORMAT = 'output format, one of: {0}; default: "%(default)s"'.format(
    ', '.join(['"' + format + '"' for format in _VALID_FORMATS]))

_HELP_SUFFIX = '''limit analysis on files matching any suffix in comma
 separated LIST; shell patterns are possible; example: "py,sql"; default:
 "%(default)s"'''

_log = logging.getLogger('pygount')

#: Regular expressions for names of files to skip during analysis.
_NAME_REGEXS_TO_SKIP = [
    re.compile(pattern) for pattern in (
        r'^\..*$',
        r'^.*~$',
    )
]

#: Regular expressions for names of files to skip during analysis.
_FOLDER_REGEXS_TO_SKIP = [
    re.compile(pattern) for pattern in (
        r'^_.*$',
    )
]
_FOLDER_REGEXS_TO_SKIP.extend(_NAME_REGEXS_TO_SKIP)


def _is_path_to_skip(name, is_folder):
    assert os.sep not in name, 'name=%r' % name
    regexs_to_skip = _FOLDER_REGEXS_TO_SKIP if is_folder else _NAME_REGEXS_TO_SKIP
    return any(
        path_name_to_skip_regex.match(name) is not None
        for path_name_to_skip_regex in regexs_to_skip
    )


def _paths_and_group_to_analyze_in(folder, group):
    assert folder is not None
    assert group is not None

    for name in os.listdir(folder):
        path = os.path.join(folder, name)
        if not os.path.islink(path):
            is_folder = os.path.isdir(path)
            if _is_path_to_skip(os.path.basename(path), is_folder):
                _log.debug('skip due matching skip pattern: %s', path)
            elif is_folder:
                yield from _paths_and_group_to_analyze_in(path, group)
            else:
                yield path, group


def _paths_and_group_to_analyze(path_to_analyse_pattern, group=None):
    for path_to_analyse in glob.glob(path_to_analyse_pattern):
        if os.path.islink(path_to_analyse):
            _log.debug('skip link: %s', path_to_analyse)
        else:
            is_folder = os.path.isdir(path_to_analyse)
            if _is_path_to_skip(os.path.basename(path_to_analyse), is_folder):
                _log.debug('skip due matching skip pattern: %s', path_to_analyse)
            else:
                actual_group = group
                if is_folder:
                    if actual_group is None:
                        actual_group = os.path.basename(path_to_analyse)
                        if actual_group == '':
                            # Compensate for trailing path separator.
                            actual_group = os.path.basename(os.path.dirname(path_to_analyse))
                    yield from _paths_and_group_to_analyze_in(path_to_analyse_pattern, actual_group)
                else:
                    if actual_group is None:
                        actual_group = os.path.dirname(path_to_analyse)
                        if actual_group == '':
                            actual_group = os.path.basename(os.path.dirname(os.path.abspath(path_to_analyse)))
                    yield path_to_analyse, actual_group


def _source_paths_and_groups_to_analyze(patterns_to_analyze):
    assert patterns_to_analyze is not None
    result = []
    for pattern in patterns_to_analyze:
        try:
            result.extend(_paths_and_group_to_analyze(pattern))
        except OSError as error:
            raise OSError('cannot scan "{0}" for source files: {1}'.format(pattern, error))
    result = sorted(set(result))
    return result


def parsed_args(arguments):
    assert arguments is not None

    parser = argparse.ArgumentParser(description='count lines of code')
    parser.add_argument(
        '--encoding', '-e', default='automatic;cp1252', help=_HELP_ENCODING
    )
    parser.add_argument(
        '--format', '-f', metavar='FORMAT', choices=_VALID_FORMATS, default='sloccount',
        help=_HELP_FORMAT
    )
    parser.add_argument(
        '--out', '-o', metavar='FILE', default='STDOUT',
        help='file to write results to; use "STDOUT" for standard output; default: "%(default)s"'
    )
    parser.add_argument(
        '--suffix', '-s', metavar='LIST', default='*', help=_HELP_SUFFIX
    )
    parser.add_argument(
        'source_patterns', metavar='PATTERN', nargs='*', default=[os.getcwd()],
        help='source files and directories to scan; can use glob patterns; default: current directory')
    parser.add_argument('--verbose', '-v', action='store_true', help='explain what is being done')
    parser.add_argument('--version', action='version', version='%(prog)s ' + pygount.__version__)
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


def pygount_command(arguments=None):
    result = 1
    if arguments is None:  # pragma: no cover
        arguments = sys.argv[1:]
    args, default_encoding, fallback_encoding = parsed_args(arguments)
    if args.verbose:
        _log.setLevel(logging.INFO)
    suffixes_to_analyze = [suffix.strip() for suffix in args.suffix.split(',')]
    try:
        source_paths_and_groups_to_analyze = _source_paths_and_groups_to_analyze(args.source_patterns)

        if args.out == 'STDOUT':
            target_file = sys.stdout
            has_target_file_to_close = False
        else:
            target_file = open(args.out, 'w', encoding='utf-8', newline='')
            has_target_file_to_close = True

        if args.format == 'cloc-xml':
            writer_class = pygount.write.ClocXmlWriter
        else:
            assert args.format == 'sloccount'
            writer_class = pygount.write.LineWriter
        with writer_class(target_file) as writer:
            for source_path, group in source_paths_and_groups_to_analyze:
                suffix = os.path.splitext(source_path)[1].lstrip('.')
                is_suffix_to_analyze = any(
                    fnmatch.fnmatch(suffix, suffix_to_analyze)
                    for suffix_to_analyze in suffixes_to_analyze
                )
                if is_suffix_to_analyze:
                    statistics = pygount.analysis.source_analysis(
                        source_path, group, default_encoding, fallback_encoding)
                    if statistics is not None:
                        if statistics.language is not None:
                            writer.add(statistics)
                        else:
                            _log.info('skip due unknown language: %s', statistics.path)
                else:
                    _log.info('skip due suffix: %s', source_path)

        if has_target_file_to_close:
            try:
                target_file.close()
            except Exception as error:
                raise OSError('cannot write output to "{0}": {1}'.format(args.output, error))

        result = 0
    except KeyboardInterrupt:  # pragma: no cover
        _log.error('interrupted as requested by user')
    except OSError as error:
        _log.error(error)
    except Exception as error:
        _log.exception(error)

    return result


def main():  # pragma: no cover
    logging.basicConfig(level=logging.WARNING)
    sys.exit(pygount_command())


if __name__ == '__main__':  # pragma: no cover
    main()
