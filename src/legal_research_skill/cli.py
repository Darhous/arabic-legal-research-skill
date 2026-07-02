from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from legal_research_skill.decisions import threshold_reached
from legal_research_skill.errors import InputError, LegalResearchSkillError, UnknownValidatorError
from legal_research_skill.loader import read_json
from legal_research_skill.pipeline import available_validators, run_pipeline
from legal_research_skill.report import error_payload, report_to_json, report_to_text
from legal_research_skill.rules import RULES, get_rule
from legal_research_skill.schema_validation import research_state_errors


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
    except UnknownValidatorError as exc:
        return _print_error(str(exc), args, code="unknown_validator", exit_code=2)
    except InputError as exc:
        return _print_error(str(exc), args, code="input_error", exit_code=2)
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
    _write_or_print(text, args.output)
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


def _write_or_print(text: str, output: Path | None) -> None:
    if output is None:
        print(text, end="")
        return
    safe_output = _safe_output_path(output)
    safe_output.parent.mkdir(parents=True, exist_ok=True)
    safe_output.write_text(text, encoding="utf-8")


def _safe_output_path(output: Path) -> Path:
    root = Path.cwd().resolve()
    resolved = output.resolve()
    if resolved != root and root not in resolved.parents:
        raise InputError("Output path must stay within the current working directory.")
    return resolved


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
