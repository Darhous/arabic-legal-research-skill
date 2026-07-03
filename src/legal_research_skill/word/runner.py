from __future__ import annotations

import json
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

from legal_research_skill.word.processes import find_new_owned_word_processes, terminate_owned_process

MIN_WORD_TIMEOUT_SECONDS = 5
MAX_WORD_TIMEOUT_SECONDS = 300
DEFAULT_WORD_TIMEOUT_SECONDS = 60


def validate_timeout(timeout_seconds: int) -> int:
    if timeout_seconds < MIN_WORD_TIMEOUT_SECONDS or timeout_seconds > MAX_WORD_TIMEOUT_SECONDS:
        msg = f"Word timeout must be between {MIN_WORD_TIMEOUT_SECONDS} and {MAX_WORD_TIMEOUT_SECONDS} seconds."
        raise ValueError(msg)
    return timeout_seconds


def run_word_worker(input_path: Path, working_path: Path, *, timeout_seconds: int) -> dict[str, Any]:
    timeout_seconds = validate_timeout(timeout_seconds)
    started = time.monotonic()
    command = [
        sys.executable,
        "-m",
        "legal_research_skill.word.worker_cli",
        str(input_path),
        str(working_path),
        str(_diagnostics_path(working_path)),
    ]
    try:
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
        )
    except OSError as exc:
        return {
            "status": "FAILED",
            "input_path": str(input_path),
            "output_path": None,
            "error_code": "worker_launch_failed",
            "error": str(exc),
            "duration_seconds": round(time.monotonic() - started, 3),
            "timeout_seconds": timeout_seconds,
            "word_version": None,
            "word_validated": False,
            "evidence": {"worker_pid": None, "launch_command": command[:3]},
        }
    try:
        stdout, stderr = process.communicate(timeout=timeout_seconds)
    except subprocess.TimeoutExpired:
        diagnostics = _read_diagnostics(_diagnostics_path(working_path))
        process.terminate()
        worker_cleanup = "worker_terminated"
        try:
            process.communicate(timeout=3)
        except subprocess.TimeoutExpired:
            process.kill()
            process.communicate(timeout=3)
            worker_cleanup = "worker_killed"
        word_pid = diagnostics.get("word_pid")
        ownership_verified = bool(diagnostics.get("word_pid_ownership_verified"))
        recovery_candidates: list[dict[str, Any]] = []
        if word_pid is not None:
            word_cleanup = terminate_owned_process(word_pid, ownership_verified)
        else:
            # DispatchEx itself never returned (or never got far enough to
            # record word_pid before the timeout fired), so the normal
            # Hwnd-based identification path in the worker never ran. Fall
            # back to diffing the pre-dispatch winword.exe snapshot the
            # worker persisted to diagnostics against a fresh post-timeout
            # snapshot. Only a single, time-plausible, executable-verified
            # new winword.exe process is ever terminated; anything
            # ambiguous is reported but left running.
            before_pids = set(diagnostics.get("before_dispatch_winword_pids") or ())
            worker_started_at = diagnostics.get("worker_started_at")
            candidates = find_new_owned_word_processes(before_pids, not_before=worker_started_at)
            recovery_candidates = [identity.to_dict() for identity in candidates]
            cleanups = [terminate_owned_process(identity.pid, identity.ownership_verified) for identity in candidates]
            if not cleanups:
                word_cleanup = {"status": "owned_word_process_not_found", "pid": None, "running_after": None}
            elif len(cleanups) == 1:
                word_cleanup = cleanups[0]
            else:
                word_cleanup = {"status": "multiple_candidates_left_running", "candidates": cleanups}
        return {
            "status": "TIMEOUT",
            "input_path": str(input_path),
            "output_path": None,
            "error_code": "word_timeout",
            "error": f"Microsoft Word automation exceeded {timeout_seconds} seconds.",
            "duration_seconds": round(time.monotonic() - started, 3),
            "timeout_seconds": timeout_seconds,
            "word_version": None,
            "word_validated": False,
            "evidence": {
                "worker_pid": process.pid,
                "word_pid": word_pid,
                "word_pid_ownership_verified": ownership_verified,
                "last_checkpoint": diagnostics.get("last_checkpoint") or diagnostics.get("checkpoint"),
                "last_operation_started": diagnostics.get("last_operation_started"),
                "last_operation_completed": diagnostics.get("last_operation_completed"),
                "diagnostics_path": str(_diagnostics_path(working_path)),
                "isolated_worker": True,
                "worker_cleanup": worker_cleanup,
                "word_process_cleanup": word_cleanup,
                "word_process_recovery_candidates": recovery_candidates,
            },
        }
    result = _parse_worker_result(stdout, stderr, process.returncode, started, timeout_seconds, process.pid, input_path)
    if result.get("status") == "WORD_VALIDATED":
        _diagnostics_path(working_path).unlink(missing_ok=True)
    return result


def _parse_worker_result(
    stdout: str,
    stderr: str,
    returncode: int | None,
    started: float,
    timeout_seconds: int,
    worker_pid: int | None,
    input_path: Path,
) -> dict[str, Any]:
    try:
        result = json.loads(stdout)
    except json.JSONDecodeError:
        return {
            "status": "FAILED",
            "input_path": str(input_path),
            "output_path": None,
            "error_code": "worker_invalid_json",
            "error": stderr.strip() or stdout.strip() or f"Worker exited with code {returncode}.",
            "duration_seconds": round(time.monotonic() - started, 3),
            "timeout_seconds": timeout_seconds,
            "word_version": None,
            "word_validated": False,
            "evidence": {"worker_pid": worker_pid, "exitcode": returncode},
        }
    result["timeout_seconds"] = timeout_seconds
    result.setdefault("duration_seconds", round(time.monotonic() - started, 3))
    result.setdefault("word_validated", result.get("status") == "WORD_VALIDATED")
    result.setdefault("evidence", {})
    result["evidence"].setdefault("worker_pid", worker_pid)
    result["evidence"].setdefault("exitcode", returncode)
    if stderr.strip():
        result["evidence"].setdefault("stderr", stderr.strip())
    return result


def _diagnostics_path(working_path: Path) -> Path:
    return working_path.with_name(f".{working_path.stem}.word-diagnostics.jsonl")


def _read_diagnostics(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    last: dict[str, Any] = {}
    try:
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                last = json.loads(line)
    except (OSError, json.JSONDecodeError):
        return {"diagnostics_read_error": str(path)}
    return last
