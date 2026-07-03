from __future__ import annotations

import os

import pytest

from legal_research_skill.paths import has_extension, is_same_file_target, resolve_confined_path


def test_resolve_confined_path_accepts_path_within_root(tmp_path):
    target = tmp_path / "sub" / "file.json"
    target.parent.mkdir()
    target.write_text("{}", encoding="utf-8")
    resolved = resolve_confined_path(target, root=tmp_path)
    assert resolved == target.resolve()


def test_resolve_confined_path_rejects_path_outside_root(tmp_path):
    outside = tmp_path.parent / "escaped.json"
    with pytest.raises(ValueError, match="within the current working directory"):
        resolve_confined_path(outside, root=tmp_path)


def test_resolve_confined_path_rejects_reserved_windows_device_name(tmp_path):
    with pytest.raises(ValueError, match="reserved Windows device name"):
        resolve_confined_path(tmp_path / "CON.docx", root=tmp_path)


def test_resolve_confined_path_root_itself_is_allowed(tmp_path):
    assert resolve_confined_path(tmp_path, root=tmp_path) == tmp_path.resolve()


def test_has_extension_matches_case_insensitively():
    from pathlib import Path

    assert has_extension(Path("draft.DOCX"), ".docx") is True
    assert has_extension(Path("draft.docx"), ".DOCX") is True
    assert has_extension(Path("draft.txt"), ".docx") is False


def test_is_same_file_target_exact_resolved_match(tmp_path):
    path = tmp_path / "a.json"
    path.write_text("{}", encoding="utf-8")
    assert is_same_file_target(path, path) is True


def test_is_same_file_target_case_variant_alias_for_nonexistent_output(tmp_path):
    # pathlib.WindowsPath equality is already case-insensitive, so a
    # case-only alias of an existing input is caught even though the output
    # path doesn't exist yet (no on-disk casing to recover).
    existing = tmp_path / "Existing.json"
    existing.write_text("{}", encoding="utf-8")
    not_yet_created = tmp_path / "existing.json"
    assert is_same_file_target(existing, not_yet_created) is True


def test_is_same_file_target_hardlink_alias(tmp_path):
    original = tmp_path / "original.json"
    original.write_text("{}", encoding="utf-8")
    alias = tmp_path / "alias.json"
    try:
        os.link(original, alias)
    except OSError:
        pytest.skip("Filesystem does not support hardlinks in this environment.")
    assert is_same_file_target(original, alias) is True


def test_is_same_file_target_samefile_oserror_is_swallowed(tmp_path, monkeypatch):
    first = tmp_path / "a.json"
    second = tmp_path / "b.json"
    first.write_text("{}", encoding="utf-8")
    second.write_text("{}", encoding="utf-8")

    def raise_oserror(_a, _b):
        raise OSError("simulated samefile failure")

    monkeypatch.setattr(os.path, "samefile", raise_oserror)
    assert is_same_file_target(first, second) is False


def test_is_same_file_target_different_files_are_not_aliased(tmp_path):
    first = tmp_path / "a.json"
    second = tmp_path / "b.json"
    first.write_text("{}", encoding="utf-8")
    second.write_text("{}", encoding="utf-8")
    assert is_same_file_target(first, second) is False
