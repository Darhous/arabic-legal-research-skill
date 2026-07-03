from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from legal_research_skill.artifacts.manifest import (
    ArtifactManifest,
    file_sha256,
    manifest_to_json,
    render_config_digest,
)
from legal_research_skill.decisions import threshold_reached
from legal_research_skill.docx.render_model import RenderConfig, build_render_model
from legal_research_skill.docx.renderer import render_docx
from legal_research_skill.docx.validation import report_to_json as docx_report_to_json
from legal_research_skill.docx.validation import report_to_text as docx_report_to_text
from legal_research_skill.docx.validation import validate_docx
from legal_research_skill.errors import ArtifactError, InputError, LegalResearchSkillError, UnknownValidatorError
from legal_research_skill.loader import read_json
from legal_research_skill.models import ResearchState
from legal_research_skill.paths import has_extension, is_same_file_target, resolve_confined_path
from legal_research_skill.pipeline import available_validators, run_pipeline
from legal_research_skill.report import error_payload, report_to_json, report_to_text
from legal_research_skill.rules import RULES, get_rule
from legal_research_skill.schema_validation import artifact_manifest_errors, research_state_errors
from legal_research_skill.word.finalization import finalize_with_word
from legal_research_skill.word.runner import DEFAULT_WORD_TIMEOUT_SECONDS


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="legal-research-skill")
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate = subparsers.add_parser("validate", help="Validate a research-state JSON file.")
    validate.add_argument("input", type=Path)
    validate.add_argument("--format", choices=("json", "text"), default="text")
    validate.add_argument("--output", type=Path)
    validate.add_argument("--validator", action="append", default=[])
    validate.add_argument("--exclude-validator", action="append", default=[])
    validate.add_argument("--fail-on", choices=("warning", "low", "medium", "high", "critical"), default="high")
    validate.add_argument("--show-passed", action="store_true")
    validate.add_argument("--compact", action="store_true")

    schema = subparsers.add_parser("schema-check", help="Check research-state schema compliance.")
    schema.add_argument("input", type=Path)
    schema.add_argument("--format", choices=("json", "text"), default="text")

    subparsers.add_parser("list-validators", help="List executable validators.")

    explain = subparsers.add_parser("explain", help="Explain a local rule ID.")
    explain.add_argument("rule_id")

    render = subparsers.add_parser("render-docx", help="Render a structurally validated DOCX draft.")
    render.add_argument("input", type=Path)
    render.add_argument("--output", type=Path, required=True)
    render.add_argument("--format", choices=("json", "text"), default="text")

    validate_docx_parser = subparsers.add_parser("validate-docx", help="Validate a DOCX OPC/OOXML package.")
    validate_docx_parser.add_argument("input", type=Path)
    validate_docx_parser.add_argument("--format", choices=("json", "text"), default="text")
    validate_docx_parser.add_argument("--compact", action="store_true")

    finalize = subparsers.add_parser("finalize-word", help="Update fields and save a DOCX through Microsoft Word.")
    finalize.add_argument("input", type=Path)
    finalize.add_argument("--output", type=Path, required=True)
    finalize.add_argument("--format", choices=("json", "text"), default="text")
    finalize.add_argument("--word-timeout-seconds", type=int, default=DEFAULT_WORD_TIMEOUT_SECONDS)

    build = subparsers.add_parser(
        "build-artifact", help="Run validation, DOCX generation, DOCX validation, and manifest."
    )
    build.add_argument("input", type=Path)
    build.add_argument("--output-dir", type=Path, required=True)
    build.add_argument("--format", choices=("json", "text"), default="text")
    build.add_argument("--compact", action="store_true")
    build.add_argument("--require-word", action="store_true")
    build.add_argument("--word-timeout-seconds", type=int, default=DEFAULT_WORD_TIMEOUT_SECONDS)
    return parser


def main(argv: list[str] | None = None) -> int:
    _configure_utf8_streams()
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "validate":
            return _validate(args)
        if args.command == "schema-check":
            return _schema_check(args)
        if args.command == "list-validators":
            return _list_validators()
        if args.command == "explain":
            return _explain(args.rule_id)
        if args.command == "render-docx":
            return _render_docx(args)
        if args.command == "validate-docx":
            return _validate_docx(args)
        if args.command == "finalize-word":
            return _finalize_word(args)
        if args.command == "build-artifact":
            return _build_artifact(args)
    except UnknownValidatorError as exc:
        return _print_error(str(exc), args, code="unknown_validator", exit_code=2)
    except InputError as exc:
        return _print_error(str(exc), args, code="input_error", exit_code=2)
    except ArtifactError as exc:
        return _print_error(str(exc), args, code="artifact_error", exit_code=1)
    except LegalResearchSkillError as exc:
        return _print_error(str(exc), args, code="configuration_error", exit_code=2)
    except Exception as exc:  # pragma: no cover - defensive CLI boundary
        return _print_error(f"Unexpected internal execution error: {exc}", args, code="internal_error", exit_code=3)
    return 0


def _validate(args: argparse.Namespace) -> int:
    report = run_pipeline(args.input, only=tuple(args.validator), exclude=tuple(args.exclude_validator))
    text = (
        report_to_json(report, compact=args.compact)
        if args.format == "json"
        else report_to_text(report, show_passed=args.show_passed, compact=args.compact)
    )
    _write_or_print(text, args.output, input_path=args.input)
    threshold = "medium" if args.fail_on == "warning" else args.fail_on
    for finding in report.findings:
        if args.fail_on == "warning" or threshold_reached(finding.severity, threshold):
            return 1
    return 0


def _schema_check(args: argparse.Namespace) -> int:
    data = read_json(args.input)
    errors = research_state_errors(data)
    if args.format == "json":
        print(json.dumps({"schema_valid": not errors, "errors": errors}, ensure_ascii=False, sort_keys=True))
    elif errors:
        print("Schema check failed:")
        for error in errors:
            print(f"- {error}")
    else:
        print("Schema check passed.")
    return 1 if errors else 0


def _list_validators() -> int:
    for validator in available_validators():
        deps = ", ".join(validator.dependencies) or "none"
        rules = ", ".join(validator.rule_ids)
        print(f"{validator.name}\tdeps={deps}\trules={rules}")
    return 0


def _explain(rule_id: str) -> int:
    if rule_id not in RULES:
        print(f"Unknown rule ID: {rule_id}")
        return 2
    rule = get_rule(rule_id)
    print(f"{rule.rule_id}: {rule.title}")
    print(rule.description)
    print(f"Default severity: {rule.severity.value}")
    print(f"Default decision: {rule.decision.value}")
    print(f"Source: {rule.source}")
    print(f"Validator: {rule.validator}")
    print(f"Correction: {rule.correction}")
    print(f"Limitation: {rule.limitation}")
    return 0


def _render_docx(args: argparse.Namespace) -> int:
    output = _safe_output_path(args.output, input_path=args.input)
    if not has_extension(output, ".docx"):
        raise InputError(f"Output path must use the .docx extension: {output}")
    if output.is_dir():
        raise InputError(f"Output path is a directory, not a file: {output}")
    report = run_pipeline(args.input)
    raw = read_json(args.input)
    model = build_render_model(ResearchState(raw), report)
    render_docx(model, output)
    docx_report = validate_docx(output)
    payload = {
        "status": "DOCX_GENERATED" if docx_report.status == "pass" else "FAILED",
        "path": str(output),
        "sha256": file_sha256(output) if output.exists() else None,
        "phase3_decision": report.overall_decision.value,
        "docx_validation": docx_report.to_dict(),
        "limitations": list(model.limitations),
    }
    _emit_payload(payload, args.format)
    return 0 if docx_report.status == "pass" else 1


def _validate_docx(args: argparse.Namespace) -> int:
    report = validate_docx(args.input)
    text = docx_report_to_json(report, compact=args.compact) if args.format == "json" else docx_report_to_text(report)
    print(text, end="")
    return 0 if report.status == "pass" else 1


def _finalize_word(args: argparse.Namespace) -> int:
    output = _safe_output_path(args.output, input_path=args.input)
    result = finalize_with_word(args.input, output, timeout_seconds=args.word_timeout_seconds)
    _emit_payload(result.to_dict(), args.format)
    if result.status == "WORD_VALIDATED":
        return 0
    if result.status in {"NOT_RUN", "NOT_AVAILABLE", "TIMEOUT", "BLOCKED"}:
        return 3
    return 4


def _build_artifact(args: argparse.Namespace) -> int:
    output_dir = _safe_output_path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    validation_report = run_pipeline(args.input)
    raw = read_json(args.input)
    state = ResearchState(raw)
    config = RenderConfig()
    model = build_render_model(state, validation_report, config=config)
    pre_word = output_dir / f"{state.task_identifier}.docx"
    if is_same_file_target(args.input, pre_word):
        raise InputError(f"Artifact output path must not refer to the same file as the input path: {pre_word}")
    render_docx(model, pre_word)
    docx_report = validate_docx(pre_word)
    word_result = (
        finalize_with_word(
            pre_word,
            output_dir / f"{state.task_identifier}.word.docx",
            timeout_seconds=args.word_timeout_seconds,
        )
        if args.require_word
        else None
    )
    word_evidence = word_result.to_dict() if word_result else {"status": "NOT_RUN", "availability": "not_checked"}
    final_path = Path(word_result.output_path) if word_result and word_result.status == "WORD_VALIDATED" else None
    status = _artifact_status(docx_report.status, word_result.status if word_result else "NOT_RUN", args.require_word)
    limitations = set(model.limitations)
    if not word_result:
        limitations.add("Microsoft Word finalization was not requested; TOC and PAGE fields are not claimed updated.")
    elif word_result.status != "WORD_VALIDATED":
        limitations.add("Microsoft Word finalization did not complete; Word-specific claims are prohibited.")
    manifest = ArtifactManifest(
        input_identifier=str(args.input),
        input_digest=file_sha256(args.input),
        phase3_baseline_hash=_git_head_hash(),
        generator_version=model.generator_version,
        render_config_digest=render_config_digest(config),
        pre_word_docx_path=str(pre_word),
        pre_word_docx_digest=file_sha256(pre_word),
        word_finalized_docx_path=str(final_path) if final_path else None,
        word_finalized_docx_digest=file_sha256(final_path) if final_path else None,
        word_evidence=word_evidence,
        generated_at=config.created_at,
        validations=(validation_report.to_dict(), docx_report.to_dict()),
        allowed_claims=tuple(_allowed_claims(docx_report.status, word_result.status if word_result else "NOT_RUN")),
        prohibited_claims=tuple(_prohibited_claims(word_result.status if word_result else "NOT_RUN")),
        limitations=tuple(sorted(limitations)),
        final_artifact_status=status,
    )
    manifest_path = output_dir / "artifact-manifest.json"
    manifest_text = manifest_to_json(manifest, compact=args.compact)
    manifest_path.write_text(manifest_text, encoding="utf-8")
    errors = artifact_manifest_errors(manifest.to_dict())
    payload = manifest.to_dict() | {"manifest_path": str(manifest_path), "manifest_schema_errors": errors}
    _emit_payload(payload, args.format)
    if errors or status in {"FAILED", "BLOCKED"}:
        return 1 if not args.require_word else 3
    return 0


def _write_or_print(text: str, output: Path | None, *, input_path: Path | None = None) -> None:
    if output is None:
        print(text, end="")
        return
    safe_output = _safe_output_path(output, input_path=input_path)
    safe_output.parent.mkdir(parents=True, exist_ok=True)
    safe_output.write_text(text, encoding="utf-8")


def _emit_payload(payload: dict, output_format: str) -> None:
    if output_format == "json":
        print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
        return
    status = payload.get("status") or payload.get("final_artifact_status")
    print(f"Status: {status}")
    for key in ("path", "manifest_path", "sha256"):
        if payload.get(key):
            print(f"{key}: {payload[key]}")


def _safe_output_path(output: Path, *, input_path: Path | None = None) -> Path:
    try:
        resolved = resolve_confined_path(output)
    except ValueError as exc:
        raise InputError(str(exc).replace("Path", "Output path", 1)) from exc
    if input_path is not None and is_same_file_target(input_path, output):
        raise InputError(f"Output path must not refer to the same file as the input path: {output}")
    return resolved


def _artifact_status(docx_status: str, word_status: str, require_word: bool) -> str:
    if docx_status != "pass":
        return "FAILED"
    if word_status == "WORD_VALIDATED":
        return "WORD_VALIDATED"
    if require_word:
        return "BLOCKED"
    return "STRUCTURALLY_VALID"


def _allowed_claims(docx_status: str, word_status: str) -> list[str]:
    claims = []
    if docx_status == "pass":
        claims.extend(["DOCX generated", "DOCX structurally validated", "RTL structurally applied"])
    if word_status == "WORD_VALIDATED":
        claims.extend(["Word validated", "TOC updated", "Page numbers updated"])
    return claims


def _prohibited_claims(word_status: str) -> list[str]:
    claims = ["Legal correctness verified", "Source authenticity verified", "Final legal research accepted"]
    if word_status != "WORD_VALIDATED":
        claims.extend(["Word validated", "TOC updated", "Page numbers updated", "print-ready"])
    return claims


def _git_head_hash() -> str:
    head = Path(".git/HEAD")
    try:
        value = head.read_text(encoding="utf-8").strip()
        if value.startswith("ref:"):
            ref = Path(".git") / value.split(" ", 1)[1]
            return ref.read_text(encoding="utf-8").strip()
        return value
    except OSError:
        return "unknown"


def _print_error(message: str, args: argparse.Namespace, *, code: str, exit_code: int) -> int:
    if getattr(args, "format", "text") == "json":
        print(json.dumps(error_payload(message, code=code), ensure_ascii=False, sort_keys=True))
    else:
        print(f"Error: {message}", file=sys.stderr)
    return exit_code


def _configure_utf8_streams() -> None:
    for stream_name in ("stdout", "stderr"):
        stream = getattr(sys, stream_name)
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")


__all__ = ["build_parser", "main"]
