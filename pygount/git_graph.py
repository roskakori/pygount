import re
from typing import Optional

from pygount.analysis import SourceScanner
from pygount.git_storage import GitStorage, git_remote_url_and_revision_if_any


def compile_revisions_regex(revisions_regex_str: str) -> re:
    # TODO#112: fix regex input
    # input needs to be fixed because it does not return any matches
    return re.compile(revisions_regex_str)


class GitGraph:
    def __init__(self, source_url: str, revisions_regex_str: Optional[str] = None):
        self._revisions_regex = compile_revisions_regex(revisions_regex_str)
        self._source_url = source_url
        self._git_storage = None

    def revisions_to_analyze(self, revisions) -> list[str]:
        # TODO#112: fix regex input
        # input needs to be fixed because it does not return any matches
        return (
            list(filter(self._revisions_regex.match, map(str, revisions)))
            if self._revisions_regex is not None
            else revisions
        )

    def execute(self):
        try:
            remote_url, revision = git_remote_url_and_revision_if_any(self._source_url)
            if remote_url is not None:
                self._git_storage = GitStorage(remote_url, revision)
                self._git_storage.extract()
                self._git_storage.unshallow()
                revisions_to_analyze = self.revisions_to_analyze(self._git_storage.revisions())

                for revision in revisions_to_analyze:
                    print(revision)
                    self._git_storage.checkout(revision)
                    scanner = SourceScanner([self._git_storage.temp_folder])
                    print(list(scanner.source_paths()))
        except OSError as error:
            raise OSError(f"cannot scan for source files: {error}")

        self._git_storage.close()
