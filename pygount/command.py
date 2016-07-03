"""
Count lines of code using pygments.
"""
# Copyright (c) 2016, Thomas Aglassinger.
# All rights reserved. Distributed under the BSD License.
import argparse
import fnmatch
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

_log = pygount.log

_PATH_NAME_REGEXS_TO_IGNORE = [
    re.compile(pattern) for pattern in (
        r'^\..*$',
        r'^_.*$',
        r'^.*~$',
    )
]


def _paths_and_group_to_analyze_in(folder, group):
    assert folder is not None
    assert group is not None

    for name in os.listdir(folder):
        path = os.path.join(folder, name)
        if not os.path.islink(path):
            is_path_name_to_ignore = [
                path_name_to_ignore_regex.match(name) is not None
                for path_name_to_ignore_regex in _PATH_NAME_REGEXS_TO_IGNORE
            ]
            if not any(is_path_name_to_ignore):
                if os.path.isfile(path):
                    yield path, group
                elif os.path.isdir(path):
                    yield from _paths_and_group_to_analyze_in(path, group)


def _paths_and_group_to_analyze(folder, group=None):
    if group is None:
        actual_group = os.path.basename(folder)
        if actual_group == '':
            # Compensate for trailing path separator.
            actual_group = os.path.basename(os.path.dirname(folder))
    else:
        actual_group = group
    yield from _paths_and_group_to_analyze_in(folder, actual_group)


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
        'source_folders', metavar='DIR', nargs='*', default=[os.getcwd()],
        help='directories to scan for source files; default: current directory')
    parser.add_argument('--verbose', '-v', action='store_true', help='explain what is being done')
    parser.add_argument('--version', action='version', version='%(prog)s ' + pygount.__version__)
    args = parser.parse_args(arguments)
    if args.encoding == 'automatic':
        default_encoding = args.encoding
        fallback_encoding = 'cp1252'
    elif args.encoding == 'chardet':
        default_encoding = args.encoding
        fallback_encoding = None
    else:
        if args.encoding.startswith('automatic;'):
            first_encoding_semicolon_index = args.encoding.find(';')
            default_encoding = args.encoding[:first_encoding_semicolon_index]
            fallback_encoding = args.encoding[first_encoding_semicolon_index + 1:]
            encoding_to_check = ('fallback encoding', fallback_encoding)
        elif args.encoding == 'chardet':
            encoding_to_check = None
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
    if arguments is None:
        arguments = sys.argv[1:]
    args, default_encoding, fallback_encoding = parsed_args(arguments)
    if args.verbose:
        _log.setLevel(logging.INFO)
    suffixes_to_analyze = [suffix.strip() for suffix in args.suffix.split(',')]
    try:
        source_paths_and_groups_to_analyze = []
        for source_folder in args.source_folders:
            try:
                source_paths_and_groups_to_analyze.extend(_paths_and_group_to_analyze(source_folder))
            except OSError as error:
                raise OSError('cannot scan folder "{0}" for source files: {1}'.format(source_folder, error))
        source_paths_and_groups_to_analyze = sorted(set(source_paths_and_groups_to_analyze))

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
                    statistics = pygount.analysis.source_analysis(source_path, group, default_encoding, fallback_encoding)
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
    except KeyboardInterrupt:
        _log.error('interrupted as requested by user')
    except OSError as error:
        _log.error(error)
    except Exception as error:
        _log.exception(error)

    return result


def main():
    logging.basicConfig(level=logging.WARNING)
    sys.exit(pygount_command())


if __name__ == '__main__':
    main()
