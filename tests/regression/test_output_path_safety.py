from __future__ import annotations

import hashlib
import json
import os
import shutil

import pytest

from legal_research_skill.cli import main
from legal_research_skill.paths import is_same_file_target


def run_cli(root, monkeypatch, capsys, *args):
    monkeypatch.chdir(root)
    try:
        code = main(list(args))
    except SystemExit as exc:
        code = int(exc.code)
    captured = capsys.readouterr()
    return code, captured.out, captured.err


def _sha256(path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _copy_fixture(root, tmp_path, name="input.json"):
    """Copy the tracked minimal-valid fixture into a scratch file.

    Regression reproductions must never touch a tracked git fixture directly
    (see CLI-1 remediation notes): always operate on an isolated copy.
    """
    source = root / "examples" / "fixtures" / "valid" / "minimal-valid.json"
    destination = tmp_path / name
    shutil.copyfile(source, destination)
    return destination


# --- CLI-1 regression: render-docx must never overwrite its own input -----


def test_render_docx_rejects_exact_same_path(root, monkeypatch, capsys, tmp_path):
    target = _copy_fixture(root, tmp_path)
    before_hash = _sha256(target)
    before_bytes = target.read_bytes()

    monkeypatch.chdir(tmp_path)
    code, _out, err = run_cli(tmp_path, monkeypatch, capsys, "render-docx", str(target), "--output", str(target))

    assert code == 2
    assert "same file as the input path" in err
    assert target.read_bytes() == before_bytes
    assert _sha256(target) == before_hash


def test_render_docx_rejects_relative_alias_of_absolute_input(root, monkeypatch, capsys, tmp_path):
    subdir = tmp_path / "work"
    subdir.mkdir()
    target = _copy_fixture(root, subdir)
    before_bytes = target.read_bytes()

    monkeypatch.chdir(tmp_path)
    relative_output = "work/../work/input.json"
    code, _out, err = run_cli(tmp_path, monkeypatch, capsys, "render-docx", str(target), "--output", relative_output)

    assert code == 2
    assert "same file as the input path" in err
    assert target.read_bytes() == before_bytes


@pytest.mark.skipif(os.name != "nt", reason="Case-insensitive aliasing is a Windows-filesystem concern.")
def test_render_docx_rejects_case_variant_alias_on_windows(root, monkeypatch, capsys, tmp_path):
    target = _copy_fixture(root, tmp_path, name="CaseSample.json")
    before_bytes = target.read_bytes()

    monkeypatch.chdir(tmp_path)
    # Same file, different case, and it does not exist yet under this casing,
    # so Path.resolve() alone (no case normalization for non-existent paths)
    # would not catch this without the explicit casefold comparison.
    aliased_output = str(tmp_path / "casesample.json")
    code, _out, err = run_cli(tmp_path, monkeypatch, capsys, "render-docx", str(target), "--output", aliased_output)

    assert code == 2
    assert "same file as the input path" in err
    assert target.read_bytes() == before_bytes


@pytest.mark.skipif(os.name != "nt", reason="Hardlink behavior exercised here targets Windows semantics.")
def test_render_docx_rejects_hardlink_alias(root, monkeypatch, capsys, tmp_path):
    target = _copy_fixture(root, tmp_path, name="original.json")
    alias = tmp_path / "hardlinked.json"
    try:
        os.link(target, alias)
    except OSError:
        pytest.skip("Filesystem does not support hardlinks in this environment.")
    before_bytes = target.read_bytes()

    monkeypatch.chdir(tmp_path)
    code, _out, err = run_cli(tmp_path, monkeypatch, capsys, "render-docx", str(target), "--output", str(alias))

    assert code == 2
    assert "same file as the input path" in err
    assert target.read_bytes() == before_bytes


def test_render_docx_succeeds_for_genuinely_different_output(root, monkeypatch, capsys, tmp_path):
    target = _copy_fixture(root, tmp_path)
    monkeypatch.chdir(tmp_path)
    output = tmp_path / "rendered.docx"
    code, out, _err = run_cli(
        tmp_path, monkeypatch, capsys, "render-docx", str(target), "--output", str(output), "--format", "json"
    )
    assert code == 0
    assert json.loads(out)["status"] == "DOCX_GENERATED"
    assert output.exists()


def test_validate_output_rejects_same_path_as_input(root, monkeypatch, capsys, tmp_path):
    target = _copy_fixture(root, tmp_path)
    before_bytes = target.read_bytes()
    monkeypatch.chdir(tmp_path)
    code, out, _err = run_cli(
        tmp_path, monkeypatch, capsys, "validate", str(target), "--format", "json", "--output", str(target)
    )
    assert code == 2
    payload = json.loads(out)
    assert payload["error"]["code"] == "input_error"
    assert "same file as the input path" in payload["error"]["message"]
    assert target.read_bytes() == before_bytes


def test_build_artifact_rejects_when_derived_docx_path_equals_input(root, monkeypatch, capsys, tmp_path):
    # A user could mistakenly point --input at a file that already carries
    # the .docx extension the tool is about to derive from task_identifier
    # ("task-minimal-valid.docx"), landing in the same output directory.
    source = root / "examples" / "fixtures" / "valid" / "minimal-valid.json"
    colliding_input = tmp_path / "task-minimal-valid.docx"
    shutil.copyfile(source, colliding_input)
    before_bytes = colliding_input.read_bytes()

    monkeypatch.chdir(tmp_path)
    code, out, _err = run_cli(
        tmp_path,
        monkeypatch,
        capsys,
        "build-artifact",
        str(colliding_input),
        "--output-dir",
        str(tmp_path),
        "--format",
        "json",
    )
    assert code == 2
    payload = json.loads(out)
    assert payload["error"]["code"] == "input_error"
    assert "same file as the input path" in payload["error"]["message"]
    assert colliding_input.read_bytes() == before_bytes


def test_finalize_word_still_rejects_same_path_with_robust_check(root, monkeypatch, capsys, tmp_path):
    # finalize-word already blocked the exact-string-match case before this
    # remediation (cli.py's shared guard now catches it even earlier, before
    # finalization.py's own defense-in-depth check would run); confirm Word
    # is never invoked and the file is untouched.
    docx_bytes = b"PK\x03\x04not-a-real-docx-but-path-guard-runs-first"
    target = tmp_path / "Draft.docx"
    target.write_bytes(docx_bytes)

    monkeypatch.chdir(tmp_path)
    code, _out, err = run_cli(tmp_path, monkeypatch, capsys, "finalize-word", str(target), "--output", str(target))
    assert code == 2
    assert "same file as the input path" in err
    assert target.read_bytes() == docx_bytes


# --- Direct unit coverage of the shared paths.is_same_file_target helper --


def test_is_same_file_target_exact_match(tmp_path):
    path = tmp_path / "a.json"
    path.write_text("{}", encoding="utf-8")
    assert is_same_file_target(path, path) is True


def test_is_same_file_target_different_files(tmp_path):
    first = tmp_path / "a.json"
    second = tmp_path / "b.json"
    first.write_text("{}", encoding="utf-8")
    second.write_text("{}", encoding="utf-8")
    assert is_same_file_target(first, second) is False


def test_is_same_file_target_nonexistent_paths_are_not_falsely_aliased(tmp_path):
    first = tmp_path / "a.json"
    second = tmp_path / "b.json"
    assert is_same_file_target(first, second) is False
