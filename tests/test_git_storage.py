from pathlib import Path

from pygount.git_storage import GitStorage, git_remote_url_and_revision, is_git_url


def test_can_detect_git_url():
    assert is_git_url("git@github.com:roskakori/pygount.git")
    assert is_git_url("git@github.com:roskakori/pygount.git/v1.5.1")
    assert is_git_url("https://github.com/roskakori/pygount.git")
    assert not is_git_url("https://example.com")
    assert not is_git_url("hello world")
    assert not is_git_url("")


def test_can_extract_git_remote_url_and_revision():
    assert git_remote_url_and_revision("git@github.com:roskakori/pygount.git/v1.5.1") == (
        "git@github.com:roskakori/pygount.git",
        "v1.5.1",
    )
    assert git_remote_url_and_revision("git@github.com:roskakori/pygount.git") == (
        "git@github.com:roskakori/pygount.git",
        None,
    )
    assert git_remote_url_and_revision("git@github.com:roskakori/pygount.git/") == (
        "git@github.com:roskakori/pygount.git",
        None,
    )


def test_can_extract_and_close_and_find_files_from_cloned_git_remote_url_with_revision():
    git_storage = GitStorage("https://github.com/roskakori/pygount.git/v0.1")
    pyproject_path = Path(git_storage.temp_folder) / "pyproject.toml"
    readme_path = Path(git_storage.temp_folder) / "README.rst"
    try:
        git_storage.extract()
        assert readme_path.exists()
        assert not pyproject_path.exists()
    finally:
        git_storage.close()
    assert not readme_path.exists()
