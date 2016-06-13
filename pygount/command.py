"""
Count lines of code using pygments.
"""
import argparse
import fnmatch
import logging
import os
import re
import sys

import pygount
import pygount.analysis

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


def pygount_command(arguments=None):
    result = 1
    if arguments is None:
        arguments = sys.argv[1:]
    parser = argparse.ArgumentParser(description='count lines of code')
    parser.add_argument(
        '--encoding', '-e', default='automatic;cp1252',
        help='encoding to use when reading source code; use "automatic" to ' \
            + 'take BOMs, XML prolog and magic headers into account and ' \
            + 'fall back to UTF-8 or CP1252 if none fits; use ' \
            + '"automatic;<fallback>" to specify a different fallback ' \
            + 'encoding than CP1252; use "chardet" to let the chardet ' \
            + 'package determine the encoding; default: "%(default)s"'
    )
    parser.add_argument(
        '--suffix', '-s', metavar='LIST', default='*',
        help='limit analysis on files matching any suffix in comma separated LIST; ' \
            + 'shell patterns are possible; example: "py,sql"; default: "%(default)s"'
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
    if args.verbose:
        _log.setLevel(logging.INFO)
    suffixes_to_analyze = [suffix.strip() for suffix in args.suffix.split(',')]
    try:
        source_paths_and_groups_to_analyze = []
        for source_folder in args.source_folders:
            source_paths_and_groups_to_analyze.extend(_paths_and_group_to_analyze(source_folder))
        source_paths_and_groups_to_analyze = sorted(set(source_paths_and_groups_to_analyze))
        for source_path, group in source_paths_and_groups_to_analyze:
            suffix = os.path.splitext(source_path)[1].lstrip('.')
            is_suffix_to_analyze = any(
                fnmatch.fnmatch(suffix, suffix_to_analyze)
                for suffix_to_analyze in suffixes_to_analyze
            )
            if is_suffix_to_analyze:
                statistics = pygount.analysis.line_analysis(source_path, group, default_encoding, fallback_encoding)
                if statistics is not None:
                    if statistics.language is not None:
                        source_line_count = statistics.code + statistics.string
                        print('{0}\t{1}\t{2}\t{3}'.format(
                            source_line_count, statistics.language, statistics.group, statistics.path))
                    else:
                        _log.info('skip due unknown language: %s', statistics.path)
            else:
                _log.info('skip due suffix: %s', source_path)

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
