from __future__ import annotations

import importlib
import json
import os
import platform
import time
from contextlib import suppress
from pathlib import Path
from typing import Any

from legal_research_skill.word.processes import identify_word_process, process_snapshot, word_pid_from_hwnd


def word_worker_entry(input_path: str, working_path: str, diagnostics_path: str | None = None) -> dict[str, Any]:
    started = time.monotonic()
    app = None
    document = None
    com_initialized = False
    pythoncom = None
    word_version = None
    diagnostics = _Diagnostics(diagnostics_path)
    evidence: dict[str, Any] = {
        "fields_updated": False,
        "toc_updated": False,
        "repaginated": False,
        "saved": False,
        "reopened": False,
        "isolated_worker": True,
        "uses_dispatch_ex": True,
        "worker_pid": os.getpid(),
        "word_pid": None,
        "word_pid_ownership_verified": False,
        "word_process_identity": None,
    }
    try:
        if platform.system().lower() != "windows":
            return _result(
                "NOT_AVAILABLE", input_path, None, started, "not_windows", "Microsoft Word requires Windows."
            )
        try:
            client = importlib.import_module("win32com.client")
            pythoncom = importlib.import_module("pythoncom")
        except ImportError as exc:
            return _result("NOT_AVAILABLE", input_path, None, started, "pywin32_missing", str(exc))
        try:
            pythoncom.CoInitializeEx(pythoncom.COINIT_APARTMENTTHREADED)
            com_initialized = True
            before_dispatch = process_snapshot()
            diagnostics.started("dispatch", evidence)
            app = client.DispatchEx("Word.Application")
            diagnostics.completed("word_instance_created", evidence)
            word_version = str(getattr(app, "Version", "") or "") or None
            app.Visible = False
            app.DisplayAlerts = 0
            with suppress(Exception):
                app.ScreenUpdating = False
            with suppress(Exception):
                app.AutomationSecurity = 3
            identity = identify_word_process(word_pid_from_hwnd(getattr(app, "Hwnd", None)), before_dispatch)
            if identity is not None:
                evidence["word_pid"] = identity.pid
                evidence["word_pid_ownership_verified"] = identity.ownership_verified
                evidence["word_process_identity"] = identity.to_dict()
                diagnostics.completed("word_pid_identified", evidence)
        except Exception as exc:
            return _result("NOT_AVAILABLE", input_path, None, started, "word_dispatch_failed", str(exc))

        try:
            diagnostics.started("document_open", evidence)
            document = app.Documents.Open(
                FileName=str(Path(working_path).resolve()),
                ConfirmConversions=False,
                ReadOnly=False,
                AddToRecentFiles=False,
                Revert=False,
                Visible=False,
                OpenAndRepair=False,
                NoEncodingDialog=True,
            )
            diagnostics.completed("document_opened", evidence)
        except Exception as exc:
            return _result("FAILED", input_path, working_path, started, "word_open_failed", str(exc), word_version)
        try:
            diagnostics.started("fields_update", evidence)
            document.Fields.Update()
            evidence["fields_updated"] = True
            diagnostics.completed("fields_updated", evidence)
            diagnostics.started("toc_update", evidence)
            for toc in document.TablesOfContents:
                toc.Update()
            evidence["toc_updated"] = True
            diagnostics.completed("toc_updated", evidence)
            diagnostics.started("repagination", evidence)
            document.Repaginate()
            evidence["repaginated"] = True
            diagnostics.completed("repaginated", evidence)
            diagnostics.started("save", evidence)
            document.Save()
            evidence["saved"] = True
            diagnostics.completed("saved", evidence)
        except Exception as exc:
            return _result(
                "FAILED",
                input_path,
                working_path,
                started,
                _update_error_code(evidence),
                str(exc),
                word_version,
                evidence,
            )
        finally:
            if document is not None:
                with suppress(Exception):
                    diagnostics.started("close", evidence)
                    document.Close(False)
                    diagnostics.completed("closed", evidence)
                document = None

        try:
            diagnostics.started("reopen", evidence)
            reopened = app.Documents.Open(
                FileName=str(Path(working_path).resolve()),
                ConfirmConversions=False,
                ReadOnly=True,
                AddToRecentFiles=False,
                Revert=False,
                Visible=False,
                OpenAndRepair=False,
                NoEncodingDialog=True,
            )
            diagnostics.completed("reopened", evidence)
            diagnostics.started("final_close", evidence)
            reopened.Close(False)
            diagnostics.completed("final_closed", evidence)
            evidence["reopened"] = True
        except Exception as exc:
            return _result(
                "FAILED",
                input_path,
                working_path,
                started,
                "word_reopen_failed",
                str(exc),
                word_version,
                evidence,
            )
        return _result("WORD_VALIDATED", input_path, working_path, started, None, None, word_version, evidence, True)
    finally:
        if document is not None:
            with suppress(Exception):
                diagnostics.started("close", evidence)
                document.Close(False)
                diagnostics.completed("closed", evidence)
        if app is not None:
            with suppress(Exception):
                diagnostics.started("quit", evidence)
                app.Quit()
                diagnostics.completed("quit_completed", evidence)
        if com_initialized and pythoncom is not None:
            with suppress(Exception):
                pythoncom.CoUninitialize()


def _update_error_code(evidence: dict[str, Any]) -> str:
    if not evidence["fields_updated"]:
        return "word_fields_update_failed"
    if not evidence["toc_updated"]:
        return "word_toc_update_failed"
    if not evidence["repaginated"]:
        return "word_repaginate_failed"
    return "word_save_failed"


def _result(
    status: str,
    input_path: str,
    output_path: str | None,
    started: float,
    error_code: str | None,
    error: str | None,
    word_version: str | None = None,
    evidence: dict[str, Any] | None = None,
    word_validated: bool = False,
) -> dict[str, Any]:
    evidence = evidence or {}
    return {
        "status": status,
        "input_path": input_path,
        "output_path": output_path,
        "error_code": error_code,
        "error": error,
        "duration_seconds": round(time.monotonic() - started, 3),
        "timeout_seconds": None,
        "word_version": word_version,
        "word_validated": word_validated,
        "evidence": evidence,
    }


class _Diagnostics:
    def __init__(self, path: str | None) -> None:
        self.path = Path(path).resolve() if path else None
        self.last_started: str | None = None
        self.last_completed: str | None = None

    def started(self, operation: str, evidence: dict[str, Any]) -> None:
        checkpoint = f"{operation}_started"
        self.last_started = checkpoint
        evidence["last_checkpoint"] = checkpoint
        evidence["last_operation_started"] = checkpoint
        self._write(checkpoint, "started", evidence)

    def completed(self, checkpoint: str, evidence: dict[str, Any]) -> None:
        self.last_completed = checkpoint
        evidence["last_checkpoint"] = checkpoint
        evidence["last_operation_completed"] = checkpoint
        self._write(checkpoint, "completed", evidence)

    def _write(self, checkpoint: str, event: str, evidence: dict[str, Any]) -> None:
        if self.path is None:
            return
        payload = {
            "timestamp": time.time(),
            "checkpoint": checkpoint,
            "event": event,
            "worker_pid": os.getpid(),
            "word_pid": evidence.get("word_pid"),
            "word_pid_ownership_verified": evidence.get("word_pid_ownership_verified"),
            "last_operation_started": self.last_started,
            "last_operation_completed": self.last_completed,
        }
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(payload, ensure_ascii=False, sort_keys=True) + "\n")
            handle.flush()
