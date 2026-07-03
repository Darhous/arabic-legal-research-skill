from __future__ import annotations

import subprocess

import pytest

TEXT_GLOBS = ("*.py", "*.json", "*.toml", "*.yml", "*.yaml", "*.md", "*.cfg", "*.ini")


def _tracked_text_files(root):
    result = subprocess.run(
        ["git", "ls-files", *TEXT_GLOBS],
        cwd=root,
        capture_output=True,
        text=True,
        check=True,
    )
    return [root / line for line in result.stdout.splitlines() if line.strip()]


def test_gitattributes_declares_lf_for_tracked_text_types(root):
    # REL-2 remediation: without an explicit policy, core.autocrlf plus a
    # missing .gitattributes made wheel builds non-reproducible across
    # checkout environments (a fresh worktree could produce CRLF source
    # where an existing checkout had LF, changing the wheel hash with no
    # content change). This guards against the policy file disappearing.
    gitattributes = root / ".gitattributes"
    assert gitattributes.is_file()
    content = gitattributes.read_text(encoding="utf-8")
    assert "eol=lf" in content
    for pattern in ("*.py", "*.json"):
        assert pattern in content


@pytest.mark.parametrize("extension", ["py", "json", "toml", "yml", "yaml", "md"])
def test_tracked_text_files_do_not_currently_contain_crlf(root, extension):
    files = [f for f in _tracked_text_files(root) if f.suffix == f".{extension}"]
    offenders = [f for f in files if b"\r\n" in f.read_bytes()]
    assert offenders == [], f"CRLF line endings found in tracked .{extension} files: {offenders}"
