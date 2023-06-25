from pathlib import Path

from pygount.git_storage import GitStorage, git_remote_url_and_revision_if_any


def test_can_extract_git_remote_url_and_revision_if_any():
    assert git_remote_url_and_revision_if_any("hello") == (None, None)
    assert git_remote_url_and_revision_if_any("git@github.com:roskakori/pygount.git/v1.5.1") == (
        "git@github.com:roskakori/pygount.git",
        "v1.5.1",
    )
    assert git_remote_url_and_revision_if_any("git@github.com:roskakori/pygount.git") == (
        "git@github.com:roskakori/pygount.git",
        None,
    )
    assert git_remote_url_and_revision_if_any("git@github.com:roskakori/pygount.git/") == (
        "git@github.com:roskakori/pygount.git",
        None,
    )
    assert git_remote_url_and_revision_if_any("") == (None, None)


def test_can_extract_and_close_and_find_files_from_cloned_git_remote_url_with_revision():
    remote_url, revision = git_remote_url_and_revision_if_any("https://github.com/roskakori/pygount.git/v0.1")
    assert remote_url is not None
    git_storage = GitStorage(remote_url, revision)
    pyproject_path = Path(git_storage.temp_folder) / "pyproject.toml"
    readme_path = Path(git_storage.temp_folder) / "README.rst"
    try:
        git_storage.extract()
        assert readme_path.exists()
        assert not pyproject_path.exists()
    finally:
        git_storage.close()
    assert not readme_path.exists()
