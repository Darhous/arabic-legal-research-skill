from __future__ import annotations

import json

from legal_research_skill.word import processes, runner
from legal_research_skill.word.processes import ProcessIdentity, find_new_owned_word_processes

# --- Unit coverage of find_new_owned_word_processes (WORD-1 fix) ----------


def test_no_new_word_process_yields_no_candidates(monkeypatch):
    monkeypatch.setattr(processes, "winword_pids", lambda: set())
    assert find_new_owned_word_processes(before_pids=set()) == []


def test_preexisting_word_process_is_never_a_candidate(monkeypatch):
    # A Word process the user already had open before our worker ran must
    # never be treated as "new" just because it is still running afterward.
    monkeypatch.setattr(processes, "winword_pids", lambda: {4242})
    candidates = find_new_owned_word_processes(before_pids={4242})
    assert candidates == []


def test_single_new_word_process_with_valid_timing_is_verified(monkeypatch):
    monkeypatch.setattr(processes, "winword_pids", lambda: {9001})
    monkeypatch.setattr(processes, "_query_process_image", lambda _pid: r"C:\Program Files\Office\WINWORD.EXE")
    monkeypatch.setattr(processes, "process_creation_time", lambda _pid: 1_000_100.0)
    candidates = find_new_owned_word_processes(before_pids=set(), not_before=1_000_000.0)
    assert len(candidates) == 1
    assert candidates[0].pid == 9001
    assert candidates[0].ownership_verified is True
    assert candidates[0].verification_error is None


def test_new_process_with_creation_time_before_worker_start_is_unverified(monkeypatch):
    monkeypatch.setattr(processes, "winword_pids", lambda: {9001})
    monkeypatch.setattr(processes, "_query_process_image", lambda _pid: r"C:\Program Files\Office\WINWORD.EXE")
    # Predates the worker start window: cannot plausibly be ours.
    monkeypatch.setattr(processes, "process_creation_time", lambda _pid: 900.0)
    candidates = find_new_owned_word_processes(before_pids=set(), not_before=1_000_000.0)
    assert len(candidates) == 1
    assert candidates[0].ownership_verified is False
    assert "creation time" in candidates[0].verification_error


def test_new_pid_that_no_longer_resolves_to_winword_is_unverified(monkeypatch):
    # PID reuse: by the time we query it, the executable is something else.
    monkeypatch.setattr(processes, "winword_pids", lambda: {9001})
    monkeypatch.setattr(processes, "_query_process_image", lambda _pid: r"C:\Windows\System32\notepad.exe")
    monkeypatch.setattr(processes, "process_creation_time", lambda _pid: None)
    candidates = find_new_owned_word_processes(before_pids=set())
    assert len(candidates) == 1
    assert candidates[0].ownership_verified is False
    assert "winword.exe" in candidates[0].verification_error


def test_multiple_new_word_processes_are_all_left_unverified(monkeypatch):
    # Ambiguous: cannot tell which (if any) of several simultaneously-new
    # winword.exe processes belongs to this worker, so none are trusted.
    monkeypatch.setattr(processes, "winword_pids", lambda: {9001, 9002})
    monkeypatch.setattr(processes, "_query_process_image", lambda _pid: r"C:\Program Files\Office\WINWORD.EXE")
    monkeypatch.setattr(processes, "process_creation_time", lambda _pid: None)
    candidates = find_new_owned_word_processes(before_pids=set())
    assert len(candidates) == 2
    assert all(candidate.ownership_verified is False for candidate in candidates)
    assert all("disambiguat" in candidate.verification_error for candidate in candidates)


def test_process_creation_time_returns_none_off_windows(monkeypatch):
    monkeypatch.setattr(processes, "is_windows", lambda: False)
    assert processes.process_creation_time(123) is None


def test_process_creation_time_returns_none_when_open_process_fails(monkeypatch):
    monkeypatch.setattr(processes, "is_windows", lambda: True)
    monkeypatch.setattr(processes, "_open_process", lambda _access, _pid: None)
    assert processes.process_creation_time(123) is None


# --- Integration coverage of the runner timeout fallback path -------------


class FakeTimeoutProcess:
    """A worker subprocess that never returns until terminate() is called.

    Mirrors the real subprocess.Popen contract: the first communicate()
    (waiting for the worker) times out; the second (reaping after
    terminate()) succeeds, matching a worker that dies promptly once
    signalled.
    """

    def __init__(self):
        self.pid = 4321
        self.terminate_called = False
        self.kill_called = False
        self._communicate_calls = 0

    def communicate(self, timeout=None):
        self._communicate_calls += 1
        if self._communicate_calls == 1:
            raise runner.subprocess.TimeoutExpired("cmd", timeout)
        return "", ""

    def terminate(self):
        self.terminate_called = True

    def kill(self):
        self.kill_called = True


def _write_predispatch_diagnostics(path, *, before_pids, worker_started_at):
    path.write_text(
        json.dumps(
            {
                "checkpoint": "dispatch_started",
                "last_operation_started": "dispatch_started",
                "last_operation_completed": None,
                "word_pid": None,
                "word_pid_ownership_verified": False,
                "before_dispatch_winword_pids": sorted(before_pids),
                "worker_started_at": worker_started_at,
            }
        )
        + "\n",
        encoding="utf-8",
    )


def test_runner_recovers_single_orphan_when_dispatch_never_returns(monkeypatch, tmp_path):
    process = FakeTimeoutProcess()
    monkeypatch.setattr("legal_research_skill.word.runner.subprocess.Popen", lambda *_a, **_k: process)
    diagnostics = runner._diagnostics_path(tmp_path / "work.docx")
    _write_predispatch_diagnostics(diagnostics, before_pids=set(), worker_started_at=1_000_000.0)

    def fake_find(before_pids, *, not_before=None):
        assert before_pids == set()
        assert not_before == 1_000_000.0
        return [
            ProcessIdentity(
                pid=9001,
                executable_path=r"C:\Program Files\Office\WINWORD.EXE",
                executable_name="WINWORD.EXE",
                existed_before_dispatch=False,
                ownership_verified=True,
            )
        ]

    monkeypatch.setattr("legal_research_skill.word.runner.find_new_owned_word_processes", fake_find)
    monkeypatch.setattr(
        "legal_research_skill.word.runner.terminate_owned_process",
        lambda pid, verified: {"status": "owned_word_process_terminated", "pid": pid, "verified": verified},
    )

    result = runner.run_word_worker(tmp_path / "input.docx", tmp_path / "work.docx", timeout_seconds=5)

    assert result["status"] == "TIMEOUT"
    assert result["evidence"]["word_pid"] is None
    assert result["evidence"]["word_process_cleanup"]["status"] == "owned_word_process_terminated"
    assert result["evidence"]["word_process_cleanup"]["pid"] == 9001
    assert result["evidence"]["word_process_recovery_candidates"][0]["pid"] == 9001


def test_runner_reports_no_candidates_without_terminating_anything(monkeypatch, tmp_path):
    process = FakeTimeoutProcess()
    monkeypatch.setattr("legal_research_skill.word.runner.subprocess.Popen", lambda *_a, **_k: process)
    diagnostics = runner._diagnostics_path(tmp_path / "work.docx")
    _write_predispatch_diagnostics(diagnostics, before_pids=set(), worker_started_at=1_000_000.0)
    monkeypatch.setattr("legal_research_skill.word.runner.find_new_owned_word_processes", lambda *_a, **_k: [])
    terminate_calls = []
    monkeypatch.setattr(
        "legal_research_skill.word.runner.terminate_owned_process",
        lambda pid, verified: terminate_calls.append((pid, verified)),
    )

    result = runner.run_word_worker(tmp_path / "input.docx", tmp_path / "work.docx", timeout_seconds=5)

    assert result["evidence"]["word_process_cleanup"]["status"] == "owned_word_process_not_found"
    assert terminate_calls == []


def test_runner_leaves_ambiguous_multi_candidates_running(monkeypatch, tmp_path):
    process = FakeTimeoutProcess()
    monkeypatch.setattr("legal_research_skill.word.runner.subprocess.Popen", lambda *_a, **_k: process)
    diagnostics = runner._diagnostics_path(tmp_path / "work.docx")
    _write_predispatch_diagnostics(diagnostics, before_pids=set(), worker_started_at=1_000_000.0)

    candidates = [
        ProcessIdentity(
            pid=9001,
            executable_path="a",
            executable_name="WINWORD.EXE",
            existed_before_dispatch=False,
            ownership_verified=False,
            verification_error="ambiguous",
        ),
        ProcessIdentity(
            pid=9002,
            executable_path="b",
            executable_name="WINWORD.EXE",
            existed_before_dispatch=False,
            ownership_verified=False,
            verification_error="ambiguous",
        ),
    ]
    monkeypatch.setattr("legal_research_skill.word.runner.find_new_owned_word_processes", lambda *_a, **_k: candidates)
    monkeypatch.setattr(
        "legal_research_skill.word.runner.terminate_owned_process",
        lambda pid, verified: {"status": "word_process_ownership_unverified", "pid": pid, "running_after": True},
    )

    result = runner.run_word_worker(tmp_path / "input.docx", tmp_path / "work.docx", timeout_seconds=5)

    cleanup = result["evidence"]["word_process_cleanup"]
    assert cleanup["status"] == "multiple_candidates_left_running"
    assert len(cleanup["candidates"]) == 2
    assert all(entry["status"] == "word_process_ownership_unverified" for entry in cleanup["candidates"])
    assert len(result["evidence"]["word_process_recovery_candidates"]) == 2
