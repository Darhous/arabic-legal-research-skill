from __future__ import annotations

import json
import types
from pathlib import Path

from legal_research_skill.cli import main
from legal_research_skill.schema_validation import artifact_manifest_errors


def run_cli(root, monkeypatch, capsys, *args):
    monkeypatch.chdir(root)
    try:
        code = main(list(args))
    except SystemExit as exc:
        code = int(exc.code)
    captured = capsys.readouterr()
    return code, captured.out, captured.err


def test_render_and_validate_docx_cli(root, monkeypatch, capsys):
    output = root / "tests_tmp" / "cli-render.docx"
    output.unlink(missing_ok=True)
    code, out, _err = run_cli(
        root,
        monkeypatch,
        capsys,
        "render-docx",
        "examples/fixtures/valid/approved-plan-locked.json",
        "--output",
        str(output),
        "--format",
        "json",
    )
    assert code == 0
    assert json.loads(out)["status"] == "DOCX_GENERATED"
    code, out, _err = run_cli(root, monkeypatch, capsys, "validate-docx", str(output), "--format", "json")
    assert code == 0
    assert json.loads(out)["status"] == "pass"
    output.unlink(missing_ok=True)


def test_build_artifact_writes_manifest_with_schema(root, monkeypatch, capsys):
    output_dir = root / "tests_tmp" / "artifact"
    _clean_dir(output_dir)
    code, out, _err = run_cli(
        root,
        monkeypatch,
        capsys,
        "build-artifact",
        "examples/fixtures/valid/approved-plan-locked.json",
        "--output-dir",
        str(output_dir),
        "--format",
        "json",
    )
    payload = json.loads(out)
    assert code == 0
    assert payload["final_artifact_status"] == "STRUCTURALLY_VALID"
    assert "print-ready" in payload["prohibited_claims"]
    manifest_path = Path(payload["manifest_path"])
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert artifact_manifest_errors(manifest) == []
    assert (output_dir / "task-approved-plan-locked.docx").exists()


def test_build_artifact_require_word_returns_word_gate_code(root, monkeypatch, capsys):
    output_dir = root / "tests_tmp" / "artifact-word"
    _clean_dir(output_dir)
    monkeypatch.setattr(
        "legal_research_skill.cli.finalize_with_word",
        lambda _input, _output, *, timeout_seconds: types.SimpleNamespace(
            status="NOT_RUN",
            output_path=None,
            to_dict=lambda: {"status": "NOT_RUN", "error": "missing Word"},
        ),
    )
    code, out, _err = run_cli(
        root,
        monkeypatch,
        capsys,
        "build-artifact",
        "examples/fixtures/valid/approved-plan-locked.json",
        "--output-dir",
        str(output_dir),
        "--require-word",
        "--format",
        "json",
    )
    payload = json.loads(out)
    assert code == 3
    assert payload["final_artifact_status"] == "BLOCKED"


def test_build_artifact_require_word_uses_generated_docx_and_can_validate(root, monkeypatch, capsys):
    output_dir = root / "tests_tmp" / "artifact-word-success"
    _clean_dir(output_dir)
    seen = {}

    def fake_finalize(input_path, output_path, *, timeout_seconds):
        seen["input_path"] = input_path
        seen["output_path"] = output_path
        seen["timeout_seconds"] = timeout_seconds
        output_path.write_bytes(input_path.read_bytes())
        return types.SimpleNamespace(
            status="WORD_VALIDATED",
            output_path=str(output_path),
            to_dict=lambda: {
                "status": "WORD_VALIDATED",
                "input_path": str(input_path),
                "output_path": str(output_path),
                "word_validated": True,
            },
        )

    monkeypatch.setattr("legal_research_skill.cli.finalize_with_word", fake_finalize)
    code, out, _err = run_cli(
        root,
        monkeypatch,
        capsys,
        "build-artifact",
        "examples/fixtures/valid/approved-plan-locked.json",
        "--output-dir",
        str(output_dir),
        "--require-word",
        "--word-timeout-seconds",
        "33",
        "--format",
        "json",
    )
    payload = json.loads(out)
    expected_input = output_dir / "task-approved-plan-locked.docx"
    assert code == 0
    assert payload["final_artifact_status"] == "WORD_VALIDATED"
    assert seen["input_path"] == expected_input
    assert seen["timeout_seconds"] == 33
    assert "print-ready" not in payload["allowed_claims"]


def test_render_docx_blocks_phase3_fail_and_output_traversal(root, monkeypatch, capsys):
    code, out, err = run_cli(
        root,
        monkeypatch,
        capsys,
        "render-docx",
        "examples/fixtures/invalid/unsupported-output-claim.json",
        "--output",
        "tests_tmp/blocked.docx",
        "--format",
        "json",
    )
    assert code == 1
    assert json.loads(out)["error"]["code"] == "artifact_error"
    code, _out, _err = run_cli(
        root,
        monkeypatch,
        capsys,
        "render-docx",
        "examples/fixtures/valid/approved-plan-locked.json",
        "--output",
        "../escape.docx",
    )
    assert code == 2
    assert "Output path" in _err
    assert err == ""


def test_validate_docx_text_and_finalize_word_not_run(root, monkeypatch, capsys):
    bad = root / "tests_tmp" / "bad.docx"
    bad.write_text("not a zip", encoding="utf-8")
    code, out, _err = run_cli(root, monkeypatch, capsys, "validate-docx", str(bad), "--format", "text")
    assert code == 1
    assert "invalid_zip" in out
    monkeypatch.setattr(
        "legal_research_skill.cli.finalize_with_word",
        lambda _input, _output, *, timeout_seconds: types.SimpleNamespace(
            status="NOT_RUN",
            output_path=None,
            to_dict=lambda: {"status": "NOT_RUN", "input_path": str(bad), "output_path": None},
        ),
    )
    code, out, _err = run_cli(
        root,
        monkeypatch,
        capsys,
        "finalize-word",
        str(bad),
        "--output",
        "tests_tmp/finalized.docx",
        "--format",
        "text",
    )
    assert code == 3
    assert "Status: NOT_RUN" in out
    bad.unlink(missing_ok=True)


def test_finalize_word_timeout_json_exit_code(root, monkeypatch, capsys):
    source = root / "tests_tmp" / "timeout-source.docx"
    source.write_bytes(b"fake docx")
    monkeypatch.setattr(
        "legal_research_skill.cli.finalize_with_word",
        lambda _input, _output, *, timeout_seconds: types.SimpleNamespace(
            status="TIMEOUT",
            output_path=None,
            to_dict=lambda: {
                "status": "TIMEOUT",
                "error_code": "word_timeout",
                "timeout_seconds": timeout_seconds,
                "word_validated": False,
            },
        ),
    )
    code, out, _err = run_cli(
        root,
        monkeypatch,
        capsys,
        "finalize-word",
        str(source),
        "--output",
        "tests_tmp/timeout-out.docx",
        "--word-timeout-seconds",
        "5",
        "--format",
        "json",
    )
    payload = json.loads(out)
    assert code == 3
    assert payload["status"] == "TIMEOUT"
    assert payload["error_code"] == "word_timeout"
    assert payload["timeout_seconds"] == 5
    source.unlink(missing_ok=True)


def test_build_artifact_text_output_and_compact_manifest(root, monkeypatch, capsys):
    output_dir = root / "tests_tmp" / "artifact-text"
    _clean_dir(output_dir)
    code, out, _err = run_cli(
        root,
        monkeypatch,
        capsys,
        "build-artifact",
        "examples/fixtures/valid/approved-plan-locked.json",
        "--output-dir",
        str(output_dir),
        "--compact",
    )
    assert code == 0
    assert "Status: STRUCTURALLY_VALID" in out
    manifest_text = (output_dir / "artifact-manifest.json").read_text(encoding="utf-8")
    assert "\n" in manifest_text and manifest_text.count("\n") == 1


def _clean_dir(path: Path) -> None:
    if not path.exists():
        return
    for child in path.iterdir():
        if child.is_file():
            child.unlink()
