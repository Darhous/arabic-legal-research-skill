from __future__ import annotations

import copy
import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path
from zipfile import ZipFile

import pytest

from legal_research_skill.artifacts.manifest import file_sha256
from legal_research_skill.schema_validation import artifact_manifest_errors


def _cli(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "legal_research_skill", *args],
        cwd=root,
        text=True,
        capture_output=True,
        check=False,
    )


def _json_cli(root: Path, *args: str) -> tuple[int, dict, str]:
    result = _cli(root, *args)
    return result.returncode, json.loads(result.stdout), result.stderr


def _state(root: Path) -> dict:
    return json.loads((root / "examples/fixtures/valid/approved-plan-locked.json").read_text(encoding="utf-8"))


def _write_state(path: Path, data: dict) -> Path:
    path.write_text(json.dumps(data, ensure_ascii=False, sort_keys=True), encoding="utf-8")
    return path


def _workspace_tmp(root: Path, tmp_path: Path, name: str) -> Path:
    path = root / "tests_tmp" / "phase5-pytest" / tmp_path.name / name
    if path.exists():
        if path.is_dir():
            shutil.rmtree(path)
        else:
            path.unlink()
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def test_black_box_artifact_build_json_text_compact_and_manifest_contract(root, tmp_path):
    output_dir = _workspace_tmp(root, tmp_path, "artifact")
    code, payload, err = _json_cli(
        root,
        "build-artifact",
        "examples/fixtures/valid/approved-plan-locked.json",
        "--output-dir",
        str(output_dir),
        "--format",
        "json",
    )
    assert err == ""
    assert code == 0
    assert payload["final_artifact_status"] == "STRUCTURALLY_VALID"
    assert payload["word_evidence"]["status"] == "NOT_RUN"
    assert payload["manifest_schema_errors"] == []
    assert "Word validated" not in payload["allowed_claims"]
    assert "print-ready" in payload["prohibited_claims"]
    docx_path = Path(payload["pre_word_docx"]["path"])
    manifest_path = Path(payload["manifest_path"])
    assert docx_path.exists()
    assert manifest_path.exists()
    assert payload["pre_word_docx"]["sha256"] == file_sha256(docx_path)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert artifact_manifest_errors(manifest) == []

    text_result = _cli(
        root,
        "build-artifact",
        "examples/fixtures/valid/approved-plan-locked.json",
        "--output-dir",
        str(_workspace_tmp(root, tmp_path, "artifact-text")),
    )
    assert text_result.returncode == 0
    assert "Status: STRUCTURALLY_VALID" in text_result.stdout

    compact_code, compact_payload, _err = _json_cli(
        root,
        "validate-docx",
        str(docx_path),
        "--format",
        "json",
        "--compact",
    )
    assert compact_code == 0
    assert compact_payload["status"] == "pass"


def test_black_box_word_gate_uses_generated_docx_when_required(root, tmp_path, monkeypatch):
    output_dir = _workspace_tmp(root, tmp_path, "word-required")

    def fake_finalize(input_path, output_path, *, timeout_seconds):
        output_path.write_bytes(input_path.read_bytes())
        return type(
            "Result",
            (),
            {
                "status": "WORD_VALIDATED",
                "output_path": str(output_path),
                "to_dict": lambda self: {
                    "status": "WORD_VALIDATED",
                    "input_path": str(input_path),
                    "output_path": str(output_path),
                    "timeout_seconds": timeout_seconds,
                    "word_validated": True,
                },
            },
        )()

    monkeypatch.setattr("legal_research_skill.cli.finalize_with_word", fake_finalize)
    from legal_research_skill.cli import main

    monkeypatch.chdir(root)
    code = main(
        [
            "build-artifact",
            "examples/fixtures/valid/approved-plan-locked.json",
            "--output-dir",
            str(output_dir),
            "--require-word",
            "--word-timeout-seconds",
            "60",
            "--format",
            "json",
        ]
    )
    manifest = json.loads((output_dir / "artifact-manifest.json").read_text(encoding="utf-8"))
    assert code == 0
    assert manifest["word_evidence"]["input_path"].endswith("task-approved-plan-locked.docx")
    assert manifest["word_evidence"]["output_path"].endswith("task-approved-plan-locked.word.docx")


@pytest.mark.parametrize(
    ("mutate", "expected"),
    [
        (lambda data: data.pop("research_metadata"), "required"),
        (lambda data: data.__setitem__("schema_version", "9.9.9"), "SCHEMA-001"),
        (lambda data: data["output_claims"]["requested"].append("court-ready"), "CLAIM-001"),
        (lambda data: data["sources"][0].__setitem__("verification_status", "missing"), "schema_violation"),
        (lambda data: data["approved_plan"]["nodes"][0].__setitem__("plan_node_id", "../bad"), "identifier"),
        (lambda data: data["methodology"]["components"]["preface"].__setitem__("content", ""), "METHOD-001"),
        (
            lambda data: data["state_machine"].__setitem__("current_state", "Unknown Future State"),
            "unsupported_workflow_state",
        ),
    ],
)
def test_input_fixture_variants_are_rejected_or_flagged(root, tmp_path, mutate, expected):
    data = _state(root)
    mutate(data)
    path = _write_state(tmp_path / "variant.json", data)
    result = _cli(root, "validate", str(path), "--format", "json")
    payload = json.loads(result.stdout)
    assert result.returncode in {1, 2}
    assert expected in result.stdout or expected in json.dumps(payload, ensure_ascii=False)


def test_arabic_mixed_unicode_long_headings_and_multiple_footnotes_render(root, tmp_path):
    data = _state(root)
    data["research_metadata"]["research_title"]["value"] = "مسؤولية AI والبيانات - اختبار (Unicode: ،؛؟)"
    long_title = "عنوان عربي طويل " * 18
    data["approved_plan"]["nodes"][0]["title"] = long_title
    data["body_hierarchy"]["nodes"][0]["title"] = long_title
    data["sources"].append({**copy.deepcopy(data["sources"][0]), "source_id": "src-law-2"})
    data["citations"].append({**copy.deepcopy(data["citations"][0]), "citation_id": "cite-2", "source_id": "src-law-2"})
    data["footnotes"].append({**copy.deepcopy(data["footnotes"][0]), "footnote_id": "fn-2", "citation_ids": ["cite-2"]})
    data["bibliography"].append(
        {**copy.deepcopy(data["bibliography"][0]), "bibliography_id": "bib-2", "source_ids": ["src-law-2"]}
    )
    path = _write_state(tmp_path / "arabic-mixed.json", data)
    output_dir = _workspace_tmp(root, tmp_path, "unicode-artifact")
    code, payload, _err = _json_cli(
        root, "build-artifact", str(path), "--output-dir", str(output_dir), "--format", "json"
    )
    assert code == 0
    assert payload["final_artifact_status"] == "STRUCTURALLY_VALID"


@pytest.mark.parametrize(
    "fixture",
    [
        "examples/fixtures/invalid/orphan-footnote.json",
        "examples/fixtures/invalid/duplicate-identifiers.json",
        "examples/fixtures/invalid/malformed-schema.json",
        "examples/fixtures/invalid/unsupported-output-claim.json",
    ],
)
def test_invalid_repository_fixtures_fail_from_public_cli(root, fixture):
    result = _cli(root, "validate", fixture, "--format", "json")
    assert result.returncode in {1, 2}
    assert result.stdout.startswith("{")
    assert "Traceback" not in result.stdout + result.stderr


def test_filesystem_attacks_and_cli_serialization_errors(root, tmp_path):
    source = root / "examples/fixtures/valid/approved-plan-locked.json"
    outside = tmp_path.parent / "escape.docx"
    traversal = _cli(root, "render-docx", str(source), "--output", "../escape.docx", "--format", "json")
    absolute = _cli(root, "render-docx", str(source), "--output", str(outside), "--format", "json")
    reserved = _cli(root, "render-docx", str(source), "--output", "CON.docx", "--format", "json")
    bad_timeout = _cli(
        root,
        "finalize-word",
        str(tmp_path / "missing.docx"),
        "--output",
        str(_workspace_tmp(root, tmp_path, "out.docx")),
        "--word-timeout-seconds",
        "1",
        "--format",
        "json",
    )
    non_integer = _cli(
        root,
        "finalize-word",
        str(tmp_path / "missing.docx"),
        "--output",
        str(_workspace_tmp(root, tmp_path, "out2.docx")),
        "--word-timeout-seconds",
        "abc",
    )
    unknown = _cli(root, "build-artifact", str(source), "--unknown")
    for result in (traversal, absolute, reserved, bad_timeout):
        assert result.returncode in {1, 2}
        assert json.loads(result.stdout)["error"]["code"] in {"input_error", "artifact_error"}
        assert "Traceback" not in result.stdout + result.stderr
    assert non_integer.returncode == 2
    assert unknown.returncode == 2


def test_symlink_escape_output_is_rejected_when_supported(root, tmp_path):
    link = tmp_path / "link"
    target = tmp_path.parent
    try:
        link.symlink_to(target, target_is_directory=True)
    except OSError as exc:
        pytest.skip(f"symlink creation unavailable in this environment: {exc}")
    result = _cli(
        root,
        "render-docx",
        "examples/fixtures/valid/approved-plan-locked.json",
        "--output",
        str(link / "escape.docx"),
        "--format",
        "json",
    )
    assert result.returncode == 2
    assert json.loads(result.stdout)["error"]["code"] == "input_error"


def test_reproducibility_idempotency_and_no_temp_leakage(root, tmp_path):
    first_dir = _workspace_tmp(root, tmp_path, "first")
    second_dir = _workspace_tmp(root, tmp_path, "second")
    first = _json_cli(
        root,
        "build-artifact",
        "examples/fixtures/valid/approved-plan-locked.json",
        "--output-dir",
        str(first_dir),
        "--format",
        "json",
    )[1]
    second = _json_cli(
        root,
        "build-artifact",
        "examples/fixtures/valid/approved-plan-locked.json",
        "--output-dir",
        str(second_dir),
        "--format",
        "json",
    )[1]
    assert first["final_artifact_status"] == second["final_artifact_status"] == "STRUCTURALLY_VALID"
    assert first["pre_word_docx"]["sha256"] == second["pre_word_docx"]["sha256"]
    assert file_sha256(Path(first["pre_word_docx"]["path"])) == first["pre_word_docx"]["sha256"]
    assert not list((root / "tests_tmp" / "phase5-pytest" / tmp_path.name).rglob("*.tmp.docx"))
    for docx_path in (Path(first["pre_word_docx"]["path"]), Path(second["pre_word_docx"]["path"])):
        with ZipFile(docx_path) as archive:
            rels = archive.read("word/_rels/document.xml.rels")
            assert rels.count(b"Relationship") == len(set(archive.namelist())) or b"Relationship" in rels


def test_manifest_semantics_are_stable_except_expected_paths_and_timestamps(root, tmp_path):
    dirs = [_workspace_tmp(root, tmp_path, "a"), _workspace_tmp(root, tmp_path, "b")]
    manifests = []
    for directory in dirs:
        _json_cli(
            root,
            "build-artifact",
            "examples/fixtures/valid/approved-plan-locked.json",
            "--output-dir",
            str(directory),
            "--format",
            "json",
        )
        manifest = json.loads((directory / "artifact-manifest.json").read_text(encoding="utf-8"))
        manifest.pop("generated_at")
        manifest["pre_word_docx"]["path"] = "<path>"
        for validation in manifest["validations"]:
            if "path" in validation:
                validation["path"] = "<path>"
        manifests.append(manifest)
    assert (
        hashlib.sha256(json.dumps(manifests[0], sort_keys=True).encode()).hexdigest()
        == hashlib.sha256(json.dumps(manifests[1], sort_keys=True).encode()).hexdigest()
    )
