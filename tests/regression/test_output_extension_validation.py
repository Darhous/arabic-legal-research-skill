from __future__ import annotations

import json
import shutil

from legal_research_skill.cli import main


def run_cli(root, monkeypatch, capsys, *args):
    monkeypatch.chdir(root)
    try:
        code = main(list(args))
    except SystemExit as exc:
        code = int(exc.code)
    captured = capsys.readouterr()
    return code, captured.out, captured.err


def _copy_fixture(root, tmp_path, name="input.json"):
    source = root / "examples" / "fixtures" / "valid" / "minimal-valid.json"
    destination = tmp_path / name
    shutil.copyfile(source, destination)
    return destination


def test_render_docx_rejects_non_docx_extension(root, monkeypatch, capsys, tmp_path):
    target = _copy_fixture(root, tmp_path)
    monkeypatch.chdir(tmp_path)
    code, out, _err = run_cli(
        tmp_path,
        monkeypatch,
        capsys,
        "render-docx",
        str(target),
        "--output",
        str(tmp_path / "draft.txt"),
        "--format",
        "json",
    )
    assert code == 2
    payload = json.loads(out)
    assert ".docx" in payload["error"]["message"]
    assert not (tmp_path / "draft.txt").exists()


def test_render_docx_accepts_uppercase_docx_extension(root, monkeypatch, capsys, tmp_path):
    target = _copy_fixture(root, tmp_path)
    monkeypatch.chdir(tmp_path)
    output = tmp_path / "DRAFT.DOCX"
    code, out, _err = run_cli(
        tmp_path,
        monkeypatch,
        capsys,
        "render-docx",
        str(target),
        "--output",
        str(output),
        "--format",
        "json",
    )
    assert code == 0
    assert json.loads(out)["status"] == "DOCX_GENERATED"
    assert output.exists()


def test_render_docx_accepts_double_extension_ending_in_docx(root, monkeypatch, capsys, tmp_path):
    target = _copy_fixture(root, tmp_path)
    monkeypatch.chdir(tmp_path)
    output = tmp_path / "final.draft.docx"
    code, out, _err = run_cli(
        tmp_path,
        monkeypatch,
        capsys,
        "render-docx",
        str(target),
        "--output",
        str(output),
        "--format",
        "json",
    )
    assert code == 0
    assert json.loads(out)["status"] == "DOCX_GENERATED"


def test_render_docx_rejects_fake_docx_double_extension(root, monkeypatch, capsys, tmp_path):
    # "evil.docx.exe" ends in .exe, not .docx -- must be rejected exactly
    # like any other non-.docx output, even though it contains ".docx" as a
    # substring earlier in the name.
    target = _copy_fixture(root, tmp_path)
    monkeypatch.chdir(tmp_path)
    output = tmp_path / "evil.docx.exe"
    code, _out, err = run_cli(
        tmp_path,
        monkeypatch,
        capsys,
        "render-docx",
        str(target),
        "--output",
        str(output),
    )
    assert code == 2
    assert ".docx" in err
    assert not output.exists()


def test_render_docx_rejects_directory_named_like_a_docx_file(root, monkeypatch, capsys, tmp_path):
    target = _copy_fixture(root, tmp_path)
    directory_output = tmp_path / "output.docx"
    directory_output.mkdir()
    monkeypatch.chdir(tmp_path)
    code, _out, err = run_cli(
        tmp_path,
        monkeypatch,
        capsys,
        "render-docx",
        str(target),
        "--output",
        str(directory_output),
    )
    assert code == 2
    assert "directory" in err
    assert directory_output.is_dir()


def test_finalize_word_rejects_directory_named_like_a_docx_file(root, monkeypatch, capsys, tmp_path):
    input_docx = tmp_path / "input.docx"
    input_docx.write_bytes(b"PK\x03\x04placeholder")
    directory_output = tmp_path / "out.docx"
    directory_output.mkdir()
    monkeypatch.chdir(tmp_path)
    code, _out, err = run_cli(
        tmp_path,
        monkeypatch,
        capsys,
        "finalize-word",
        str(input_docx),
        "--output",
        str(directory_output),
    )
    # This path is validated inside finalize_with_word (ArtifactError, exit
    # code 1), one layer past cli.py's own InputError-based guards (exit 2).
    assert code == 1
    assert "directory" in err
