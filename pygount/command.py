"""
Count lines of code using pygments.
"""
import argparse
import logging
import os
import sys

import pygount
import pygount.analysis

_log = pygount.log


def pygount_command(arguments=None):
    result = 1
    if arguments is None:
        arguments = sys.argv[1:]
    parser = argparse.ArgumentParser(description='count lines of code')
    parser.add_argument(
        'source_folders', metavar='DIR', nargs='*', default=[os.getcwd()],
        help='directories to scan for source files; default: current directory')
    parser.add_argument('--verbose', '-v', action='store_true', help='explain what is being done')
    parser.add_argument('--version', action='version', version='%(prog)s ' + pygount.__version__)
    args = parser.parse_args(arguments)
    if args.verbose:
        _log.setLevel(logging.INFO)
    try:
        project_and_source_paths = []
        for source_folder in args.source_folders:
            project = os.path.basename(source_folder)
            for folder, _, filenames in os.walk(source_folder):
                for filename in filenames:
                    project_and_source_paths.append((project, os.path.join(folder, filename)))
        project_and_source_paths = sorted(set(project_and_source_paths))
        for project, source_path in project_and_source_paths:
            statistics = pygount.analysis.line_analysis(project, source_path)
            if statistics is not None:
                source_line_count = statistics.code + statistics.string
                print('{0}\t{1}\t{2}\t{3}'.format(
                    source_line_count, statistics.language, statistics.project, statistics.path))
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
