from __future__ import annotations

import types

import pytest

from legal_research_skill.word import runner
from legal_research_skill.word.availability import detect_word_availability
from legal_research_skill.word.finalization import finalize_with_word
from legal_research_skill.word import processes
from legal_research_skill.word.processes import identify_word_process, terminate_owned_process
from legal_research_skill.word.worker import word_worker_entry
from legal_research_skill.word.worker_cli import main as worker_cli_main


def test_word_availability_reports_non_windows(monkeypatch):
    monkeypatch.setattr("platform.system", lambda: "Linux")
    availability = detect_word_availability()
    assert availability.status == "NOT_AVAILABLE"
    assert availability.word_available is False
    assert availability.to_dict()["status"] == "NOT_AVAILABLE"


def test_word_availability_reports_missing_pywin32(monkeypatch):
    monkeypatch.setattr("platform.system", lambda: "Windows")
    monkeypatch.setattr("importlib.import_module", lambda _name: (_ for _ in ()).throw(ImportError("missing")))
    availability = detect_word_availability()
    assert availability.com_available is False
    assert "missing" in availability.error


def test_word_availability_reports_available_and_quits(monkeypatch):
    app = FakeWordApp()
    monkeypatch.setattr("platform.system", lambda: "Windows")
    monkeypatch.setattr("importlib.import_module", lambda _name: types.SimpleNamespace(DispatchEx=lambda _prog: app))
    availability = detect_word_availability()
    assert availability.word_available is True
    assert availability.version == "16.0"
    assert app.quit_called is True


def test_word_availability_reports_dispatch_failure(monkeypatch):
    monkeypatch.setattr("platform.system", lambda: "Windows")
    monkeypatch.setattr(
        "importlib.import_module",
        lambda _name: types.SimpleNamespace(DispatchEx=lambda _prog: (_ for _ in ()).throw(RuntimeError("COM"))),
    )
    availability = detect_word_availability()
    assert availability.com_available is True
    assert availability.word_available is False
    assert "COM" in availability.error


def test_worker_success_with_fake_com(monkeypatch, tmp_path):
    app = FakeWordApp()
    monkeypatch.setattr("platform.system", lambda: "Windows")
    monkeypatch.setattr("legal_research_skill.word.worker.process_snapshot", lambda: {})
    monkeypatch.setattr("legal_research_skill.word.worker.word_pid_from_hwnd", lambda _hwnd: 5678)
    monkeypatch.setattr(
        "legal_research_skill.word.worker.identify_word_process",
        lambda _pid, _before: types.SimpleNamespace(
            pid=5678, ownership_verified=True, to_dict=lambda: {"pid": 5678, "ownership_verified": True}
        ),
    )
    monkeypatch.setattr("importlib.import_module", lambda _name: types.SimpleNamespace(DispatchEx=lambda _prog: app))
    diagnostics_path = tmp_path / "diagnostics.jsonl"
    result = word_worker_entry(str(tmp_path / "input.docx"), str(tmp_path / "work.docx"), str(diagnostics_path))
    assert result["status"] == "WORD_VALIDATED"
    assert result["word_validated"] is True
    assert result["evidence"]["word_pid"] == 5678
    assert result["evidence"]["word_pid_ownership_verified"] is True
    assert result["evidence"]["last_checkpoint"] == "quit_completed"
    assert result["evidence"]["fields_updated"] is True
    assert result["evidence"]["toc_updated"] is True
    assert result["evidence"]["reopened"] is True
    assert "document_open_started" in diagnostics_path.read_text(encoding="utf-8")
    assert app.quit_called is True
    assert app.open_count == 2


@pytest.mark.parametrize(
    ("app_kwargs", "error_code"),
    [
        ({"open_error": True}, "word_open_failed"),
        ({"fields_error": True}, "word_fields_update_failed"),
        ({"save_error": True}, "word_save_failed"),
        ({"reopen_error": True}, "word_reopen_failed"),
    ],
)
def test_worker_failure_modes_close_and_quit(monkeypatch, tmp_path, app_kwargs, error_code):
    app = FakeWordApp(**app_kwargs)
    monkeypatch.setattr("platform.system", lambda: "Windows")
    monkeypatch.setattr("importlib.import_module", lambda _name: types.SimpleNamespace(DispatchEx=lambda _prog: app))
    result = word_worker_entry(str(tmp_path / "input.docx"), str(tmp_path / "work.docx"))
    assert result["status"] == "FAILED"
    assert result["error_code"] == error_code
    assert app.quit_called is True
    if app.last_document is not None:
        assert app.last_document.closed is True


def test_worker_dispatch_failure_and_non_windows(monkeypatch, tmp_path):
    monkeypatch.setattr("platform.system", lambda: "Linux")
    assert word_worker_entry("in.docx", "work.docx")["error_code"] == "not_windows"
    monkeypatch.setattr("platform.system", lambda: "Windows")
    monkeypatch.setattr(
        "importlib.import_module",
        lambda _name: types.SimpleNamespace(DispatchEx=lambda _prog: (_ for _ in ()).throw(RuntimeError("COM"))),
    )
    result = word_worker_entry(str(tmp_path / "input.docx"), str(tmp_path / "work.docx"))
    assert result["status"] == "NOT_AVAILABLE"
    assert result["error_code"] == "word_dispatch_failed"


def test_runner_timeout_terminates_worker_only(monkeypatch, tmp_path):
    process = FakeProcess(timeouts_before_success=2)
    monkeypatch.setattr("legal_research_skill.word.runner.subprocess.Popen", lambda *_args, **_kwargs: process)
    monkeypatch.setattr(
        "legal_research_skill.word.runner.terminate_owned_process",
        lambda pid, ownership: {"status": "owned_word_process_terminated", "pid": pid, "ownership": ownership},
    )
    diagnostics = runner._diagnostics_path(tmp_path / "work.docx")
    diagnostics.write_text(
        '{"checkpoint":"document_open_started","last_operation_started":"document_open_started",'
        '"last_operation_completed":"word_instance_created","word_pid":5678,'
        '"word_pid_ownership_verified":true}\n',
        encoding="utf-8",
    )
    assert runner._read_diagnostics(diagnostics)["checkpoint"] == "document_open_started"
    result = runner.run_word_worker(tmp_path / "input.docx", tmp_path / "work.docx", timeout_seconds=5)
    assert result["status"] == "TIMEOUT"
    assert result["error_code"] == "word_timeout"
    assert process.terminate_called is True
    assert process.kill_called is True
    assert result["evidence"]["last_checkpoint"] == "document_open_started"
    assert result["evidence"]["word_pid"] == 5678
    assert result["evidence"]["word_pid_ownership_verified"] is True
    assert result["evidence"]["worker_cleanup"] == "worker_killed"
    assert result["evidence"]["word_process_cleanup"]["status"] == "owned_word_process_terminated"


def test_runner_invalid_worker_json(monkeypatch, tmp_path):
    process = FakeProcess(stdout="not-json", stderr="bad", returncode=1, timeout=False)
    monkeypatch.setattr("legal_research_skill.word.runner.subprocess.Popen", lambda *_args, **_kwargs: process)
    result = runner.run_word_worker(tmp_path / "input.docx", tmp_path / "work.docx", timeout_seconds=5)
    assert result["status"] == "FAILED"
    assert result["error_code"] == "worker_invalid_json"


def test_runner_success_deletes_diagnostics_and_records_stderr(monkeypatch, tmp_path):
    diagnostics = runner._diagnostics_path(tmp_path / "work.docx")
    diagnostics.write_text('{"checkpoint":"saved"}\n', encoding="utf-8")
    process = FakeProcess(
        stdout='{"status":"WORD_VALIDATED","evidence":{},"word_validated":true}',
        stderr="warning",
        returncode=0,
        timeout=False,
    )
    monkeypatch.setattr("legal_research_skill.word.runner.subprocess.Popen", lambda *_args, **_kwargs: process)
    result = runner.run_word_worker(tmp_path / "input.docx", tmp_path / "work.docx", timeout_seconds=5)
    assert result["status"] == "WORD_VALIDATED"
    assert result["evidence"]["stderr"] == "warning"
    assert not diagnostics.exists()


def test_runner_diagnostics_missing_and_malformed(tmp_path):
    assert runner._read_diagnostics(tmp_path / "missing.jsonl") == {}
    malformed = tmp_path / "bad.jsonl"
    malformed.write_text("{", encoding="utf-8")
    assert "diagnostics_read_error" in runner._read_diagnostics(malformed)


def test_runner_worker_launch_failure(monkeypatch, tmp_path):
    monkeypatch.setattr(
        "legal_research_skill.word.runner.subprocess.Popen",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(OSError("launch failed")),
    )
    result = runner.run_word_worker(tmp_path / "input.docx", tmp_path / "work.docx", timeout_seconds=5)
    assert result["status"] == "FAILED"
    assert result["error_code"] == "worker_launch_failed"
    assert result["word_validated"] is False


def test_process_identity_requires_new_winword_pid(monkeypatch):
    monkeypatch.setattr("legal_research_skill.word.processes.is_windows", lambda: True)
    monkeypatch.setattr(
        "legal_research_skill.word.processes._query_process_image",
        lambda _pid: r"C:\Program Files\Microsoft Office\root\Office16\WINWORD.EXE",
    )
    verified = identify_word_process(2222, {1111: {"executable_name": "WINWORD.EXE"}})
    assert verified is not None
    assert verified.ownership_verified is True
    preexisting = identify_word_process(1111, {1111: {"executable_name": "WINWORD.EXE"}})
    assert preexisting is not None
    assert preexisting.ownership_verified is False


def test_process_helpers_cover_non_windows_and_no_handle(monkeypatch):
    monkeypatch.setattr("legal_research_skill.word.processes.is_windows", lambda: False)
    assert processes.current_pid() > 0
    assert processes.process_snapshot() == {}
    assert processes.word_pid_from_hwnd(123) is None
    assert processes.is_process_running(123) is None
    assert processes.terminate_owned_process(123, True)["status"] == "cleanup_failed"
    assert processes._open_process(processes.PROCESS_QUERY_LIMITED_INFORMATION, 123) is None

    monkeypatch.setattr("legal_research_skill.word.processes.is_windows", lambda: True)
    monkeypatch.setattr("legal_research_skill.word.processes._open_process", lambda _access, _pid: None)
    assert processes.is_process_running(123) is False
    assert processes._query_process_image(123) is None
    assert processes._process_name(123) is None


def test_terminate_owned_process_pid_absent_and_not_running(monkeypatch):
    assert terminate_owned_process(None, True)["status"] == "owned_word_process_not_found"
    monkeypatch.setattr("legal_research_skill.word.processes.is_windows", lambda: True)
    monkeypatch.setattr("legal_research_skill.word.processes.is_process_running", lambda _pid: False)
    assert terminate_owned_process(5678, True)["status"] == "owned_word_process_not_found"


def test_terminate_owned_process_refuses_unverified_pid(monkeypatch):
    monkeypatch.setattr("legal_research_skill.word.processes.is_windows", lambda: True)
    monkeypatch.setattr("legal_research_skill.word.processes.is_process_running", lambda _pid: True)
    result = terminate_owned_process(5678, False)
    assert result["status"] == "word_process_ownership_unverified"
    assert result["running_after"] is True


def test_worker_cli_usage_error(capsys):
    assert worker_cli_main([]) == 2
    assert "worker_usage_error" in capsys.readouterr().out


def test_worker_cli_success_and_failure_codes(monkeypatch, capsys):
    monkeypatch.setattr(
        "legal_research_skill.word.worker_cli.word_worker_entry",
        lambda *_args: {"status": "WORD_VALIDATED", "word_validated": True},
    )
    assert worker_cli_main(["in.docx", "work.docx", "diag.jsonl"]) == 0
    assert "WORD_VALIDATED" in capsys.readouterr().out
    monkeypatch.setattr(
        "legal_research_skill.word.worker_cli.word_worker_entry",
        lambda *_args: {"status": "FAILED", "word_validated": False},
    )
    assert worker_cli_main(["in.docx", "work.docx"]) == 1


def test_runner_timeout_bounds():
    with pytest.raises(ValueError, match="between"):
        runner.validate_timeout(1)
    with pytest.raises(ValueError, match="between"):
        runner.validate_timeout(999)
    assert runner.validate_timeout(60) == 60


def test_finalize_word_path_safety_errors(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    missing = tmp_path / "missing.docx"
    with pytest.raises(Exception, match="does not exist"):
        finalize_with_word(missing, tmp_path / "out.docx")
    input_path = tmp_path / "input.docx"
    input_path.write_bytes(b"docx")
    with pytest.raises(Exception, match="must not overwrite"):
        finalize_with_word(input_path, input_path)
    with pytest.raises(Exception, match="current working directory"):
        finalize_with_word(input_path, tmp_path.parent / "outside.docx")
    with pytest.raises(Exception, match=r"\.docx"):
        finalize_with_word(input_path, tmp_path / "out.txt")
    reserved = tmp_path / "CON.docx"
    reserved.write_bytes(b"docx")
    with pytest.raises(Exception, match="reserved Windows"):
        finalize_with_word(reserved, tmp_path / "out.docx")


def test_finalize_word_success_atomic_replace_and_serialization(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    input_path = tmp_path / "input.docx"
    output_path = tmp_path / "out.docx"
    input_path.write_bytes(b"original")

    def fake_worker(_input, working, *, timeout_seconds):
        working.write_bytes(b"final")
        return _worker_result("WORD_VALIDATED", str(_input), str(working), timeout_seconds)

    monkeypatch.setattr("legal_research_skill.word.finalization.run_word_worker", fake_worker)
    monkeypatch.setattr(
        "legal_research_skill.word.finalization.validate_docx",
        lambda path: types.SimpleNamespace(status="pass", to_dict=lambda: {"status": "pass", "path": str(path)}),
    )
    result = finalize_with_word(input_path, output_path, timeout_seconds=60)
    assert result.status == "WORD_VALIDATED"
    assert output_path.read_bytes() == b"final"
    assert input_path.read_bytes() == b"original"
    assert result.to_dict()["word_validated"] is True


def test_finalize_word_failure_deletes_partial_output(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    input_path = tmp_path / "input.docx"
    output_path = tmp_path / "out.docx"
    input_path.write_bytes(b"original")

    def fake_worker(_input, working, *, timeout_seconds):
        working.write_bytes(b"partial")
        return _worker_result("TIMEOUT", str(_input), None, timeout_seconds, "word_timeout")

    monkeypatch.setattr("legal_research_skill.word.finalization.run_word_worker", fake_worker)
    result = finalize_with_word(input_path, output_path, timeout_seconds=60)
    assert result.status == "TIMEOUT"
    assert not output_path.exists()
    assert input_path.read_bytes() == b"original"
    assert not list(tmp_path.glob("*.tmp.docx"))


def test_finalize_word_temp_copy_failure_is_structured(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    input_path = tmp_path / "input.docx"
    output_path = tmp_path / "out.docx"
    input_path.write_bytes(b"original")
    monkeypatch.setattr(
        "legal_research_skill.word.finalization.shutil.copyfile",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(OSError("copy failed")),
    )
    result = finalize_with_word(input_path, output_path, timeout_seconds=60)
    assert result.status == "FAILED"
    assert result.error_code == "word_temp_copy_failed"
    assert not output_path.exists()
    assert input_path.read_bytes() == b"original"


def test_finalize_word_post_validation_failure(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    input_path = tmp_path / "input.docx"
    output_path = tmp_path / "out.docx"
    input_path.write_bytes(b"original")
    monkeypatch.setattr(
        "legal_research_skill.word.finalization.run_word_worker",
        lambda _input, working, *, timeout_seconds: _worker_result(
            "WORD_VALIDATED", str(_input), str(working), timeout_seconds
        ),
    )
    monkeypatch.setattr(
        "legal_research_skill.word.finalization.validate_docx",
        lambda path: types.SimpleNamespace(status="fail", to_dict=lambda: {"status": "fail", "path": str(path)}),
    )
    result = finalize_with_word(input_path, output_path, timeout_seconds=60)
    assert result.status == "FAILED"
    assert result.error_code == "post_word_docx_validation_failed"
    assert not output_path.exists()


def test_finalize_word_atomic_replace_failure_deletes_temp_and_preserves_input(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    input_path = tmp_path / "input.docx"
    output_path = tmp_path / "out.docx"
    input_path.write_bytes(b"original")

    def fake_worker(_input, working, *, timeout_seconds):
        working.write_bytes(b"final")
        return _worker_result("WORD_VALIDATED", str(_input), str(working), timeout_seconds)

    monkeypatch.setattr("legal_research_skill.word.finalization.run_word_worker", fake_worker)
    monkeypatch.setattr(
        "legal_research_skill.word.finalization.validate_docx",
        lambda path: types.SimpleNamespace(status="pass", to_dict=lambda: {"status": "pass", "path": str(path)}),
    )
    monkeypatch.setattr(
        "legal_research_skill.word.finalization.os.replace",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(OSError("replace failed")),
    )
    result = finalize_with_word(input_path, output_path, timeout_seconds=60)
    assert result.status == "FAILED"
    assert result.error_code == "word_atomic_replace_failed"
    assert not output_path.exists()
    assert input_path.read_bytes() == b"original"
    assert not list(tmp_path.glob("*.tmp.docx"))


def _worker_result(status, input_path, output_path, timeout_seconds, error_code=None):
    return {
        "status": status,
        "input_path": input_path,
        "output_path": output_path,
        "error_code": error_code,
        "error": None,
        "duration_seconds": 0.1,
        "timeout_seconds": timeout_seconds,
        "word_version": "16.0",
        "word_validated": status == "WORD_VALIDATED",
        "evidence": {},
    }


class FakeProcess:
    def __init__(self, stdout="", stderr="", returncode=None, timeout=False, timeouts_before_success=0):
        self.pid = 12345
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr
        self.timeout = timeout
        self.timeouts_before_success = timeouts_before_success
        self.terminate_called = False
        self.kill_called = False

    def communicate(self, timeout=None):
        if self.timeout:
            raise runner.subprocess.TimeoutExpired("cmd", timeout)
        if self.timeouts_before_success > 0:
            self.timeouts_before_success -= 1
            raise runner.subprocess.TimeoutExpired("cmd", timeout)
        return self.stdout, self.stderr

    def terminate(self):
        self.terminate_called = True

    def kill(self):
        self.kill_called = True


class FakeFields:
    def __init__(self, fail=False):
        self.fail = fail

    def Update(self):
        if self.fail:
            raise RuntimeError("field update failed")


class FakeToc:
    def __init__(self):
        self.updated = False

    def Update(self):
        self.updated = True


class FakeDocument:
    def __init__(self, fields_error=False, save_error=False):
        self.Fields = FakeFields(fields_error)
        self.TablesOfContents = [FakeToc()]
        self.closed = False
        self.save_error = save_error

    def Repaginate(self):
        return None

    def Save(self):
        if self.save_error:
            raise RuntimeError("save failed")

    def Close(self, _save):
        self.closed = True


class FakeDocuments:
    def __init__(self, app):
        self.app = app

    def Open(self, *_args, **_kwargs):
        self.app.open_count += 1
        if self.app.open_error and self.app.open_count == 1:
            raise RuntimeError("open failed")
        if self.app.reopen_error and self.app.open_count == 2:
            raise RuntimeError("reopen failed")
        doc = FakeDocument(self.app.fields_error, self.app.save_error)
        self.app.last_document = doc
        return doc


class FakeWordApp:
    Version = "16.0"

    def __init__(self, open_error=False, fields_error=False, save_error=False, reopen_error=False):
        self.open_error = open_error
        self.fields_error = fields_error
        self.save_error = save_error
        self.reopen_error = reopen_error
        self.Documents = FakeDocuments(self)
        self.open_count = 0
        self.quit_called = False
        self.last_document = None

    def Quit(self):
        self.quit_called = True
