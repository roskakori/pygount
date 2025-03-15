import re
import shutil
from tempfile import mkdtemp
from typing import Optional

import git

#: Regular expression to detect git url with the optional tag or branch
# from https://stackoverflow.com/questions/2514859/regular-expression-for-git-repository server-name
_GIT_URL_REGEX = re.compile(
    r"(?P<remote_url>((git|ssh|http(s)?)|(git@[\w.-]+))(:(//)?)([\w.@:/\-~]+)(\.git))(/)?(?P<revision>[\w./\-]+)?"
)


def git_remote_url_and_revision_if_any(git_url: str) -> tuple[Optional[str], Optional[str]]:
    assert git_url is not None
    git_url_match = _GIT_URL_REGEX.match(git_url)
    return (
        (None, None) if git_url_match is None else (git_url_match.group("remote_url"), git_url_match.group("revision"))
    )


class GitStorage:
    def __init__(self, remote_url: str, revision: Optional[str] = None):
        assert remote_url is not None
        self._remote_url = remote_url
        self._revision = revision
        self._temp_folder = mkdtemp()

    @property
    def temp_folder(self) -> str:
        return self._temp_folder

    def extract(self):
        multi_options = ["--depth", "1"]
        if self._revision is not None:
            multi_options.extend(["--branch", self._revision])
        git.Repo.clone_from(self._remote_url, self._temp_folder, multi_options=multi_options)

    def close(self):
        shutil.rmtree(self._temp_folder, ignore_errors=True)
