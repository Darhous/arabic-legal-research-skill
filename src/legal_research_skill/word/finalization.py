from __future__ import annotations

import os
import shutil
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from legal_research_skill.docx.validation import validate_docx
from legal_research_skill.errors import ArtifactError
from legal_research_skill.paths import WINDOWS_RESERVED_NAMES, has_extension, is_same_file_target
from legal_research_skill.word.runner import DEFAULT_WORD_TIMEOUT_SECONDS, run_word_worker, validate_timeout


@dataclass(frozen=True, slots=True)
class WordFinalizationResult:
    status: str
    input_path: str
    output_path: str | None
    error_code: str | None
    error: str | None
    duration_seconds: float | None
    timeout_seconds: int | None
    word_version: str | None
    word_validated: bool
    evidence: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "input_path": self.input_path,
            "output_path": self.output_path,
            "error_code": self.error_code,
            "error": self.error,
            "duration_seconds": self.duration_seconds,
            "timeout_seconds": self.timeout_seconds,
            "word_version": self.word_version,
            "word_validated": self.word_validated,
            "evidence": self.evidence,
        }


def finalize_with_word(
    input_path: Path,
    output_path: Path,
    *,
    timeout_seconds: int = DEFAULT_WORD_TIMEOUT_SECONDS,
) -> WordFinalizationResult:
    started = time.monotonic()
    timeout_seconds = _checked_timeout(timeout_seconds)
    input_resolved, output_resolved = _validate_paths(input_path, output_path)
    output_resolved.parent.mkdir(parents=True, exist_ok=True)
    temp_output = output_resolved.with_name(f".{output_resolved.stem}.word-worker.tmp.docx")
    temp_output.unlink(missing_ok=True)
    try:
        try:
            shutil.copyfile(input_resolved, temp_output)
        except OSError as exc:
            return WordFinalizationResult(
                status="FAILED",
                input_path=str(input_resolved),
                output_path=None,
                error_code="word_temp_copy_failed",
                error=str(exc),
                duration_seconds=round(time.monotonic() - started, 3),
                timeout_seconds=timeout_seconds,
                word_version=None,
                word_validated=False,
                evidence={"temp_output": str(temp_output)},
            )
        worker_result = run_word_worker(input_resolved, temp_output, timeout_seconds=timeout_seconds)
        if worker_result["status"] != "WORD_VALIDATED":
            temp_output.unlink(missing_ok=True)
            return _from_worker(worker_result, output_path=None)
        docx_report = validate_docx(temp_output)
        evidence = dict(worker_result.get("evidence", {}))
        evidence["post_word_structural_validation"] = docx_report.to_dict()
        if docx_report.status != "pass":
            temp_output.unlink(missing_ok=True)
            worker_result.update(
                {
                    "status": "FAILED",
                    "output_path": None,
                    "error_code": "post_word_docx_validation_failed",
                    "error": "DOCX structural validation failed after Word finalization.",
                    "word_validated": False,
                    "evidence": evidence,
                }
            )
            return _from_worker(worker_result, output_path=None)
        try:
            os.replace(temp_output, output_resolved)
        except OSError as exc:
            worker_result.update(
                {
                    "status": "FAILED",
                    "output_path": None,
                    "error_code": "word_atomic_replace_failed",
                    "error": str(exc),
                    "word_validated": False,
                    "evidence": evidence,
                }
            )
            return _from_worker(worker_result, output_path=None)
        worker_result.update(
            {
                "status": "WORD_VALIDATED",
                "output_path": str(output_resolved),
                "word_validated": True,
                "evidence": evidence,
                "duration_seconds": round(time.monotonic() - started, 3),
            }
        )
        return _from_worker(worker_result, output_path=output_resolved)
    finally:
        if temp_output.exists():
            temp_output.unlink(missing_ok=True)


def _checked_timeout(timeout_seconds: int) -> int:
    try:
        return validate_timeout(int(timeout_seconds))
    except ValueError as exc:
        raise ArtifactError(str(exc)) from exc


def _validate_paths(input_path: Path, output_path: Path) -> tuple[Path, Path]:
    root = Path.cwd().resolve()
    input_resolved = input_path.resolve()
    output_resolved = output_path.resolve()
    if not input_resolved.exists() or not input_resolved.is_file():
        raise ArtifactError("Input DOCX does not exist.")
    if not has_extension(input_resolved, ".docx") or not has_extension(output_resolved, ".docx"):
        raise ArtifactError("Word finalization input and output must use the .docx extension.")
    if output_resolved.is_dir():
        raise ArtifactError("Word finalization output path is a directory, not a file.")
    if is_same_file_target(input_path, output_path):
        raise ArtifactError("Word finalization output must not overwrite the input file.")
    if root not in input_resolved.parents and input_resolved != root:
        raise ArtifactError("Word finalization input path must stay within the current working directory.")
    if root not in output_resolved.parents and output_resolved != root:
        raise ArtifactError("Word finalization output path must stay within the current working directory.")
    if input_resolved.stem.upper() in WINDOWS_RESERVED_NAMES or output_resolved.stem.upper() in WINDOWS_RESERVED_NAMES:
        raise ArtifactError("Word finalization paths must not use reserved Windows device names.")
    return input_resolved, output_resolved


def _from_worker(result: dict[str, Any], *, output_path: Path | None) -> WordFinalizationResult:
    status = str(result.get("status") or "FAILED")
    return WordFinalizationResult(
        status=status,
        input_path=str(result.get("input_path") or ""),
        output_path=str(output_path) if output_path else None,
        error_code=result.get("error_code"),
        error=result.get("error"),
        duration_seconds=result.get("duration_seconds"),
        timeout_seconds=result.get("timeout_seconds"),
        word_version=result.get("word_version"),
        word_validated=bool(result.get("word_validated") and status == "WORD_VALIDATED"),
        evidence=result.get("evidence") or {},
    )
