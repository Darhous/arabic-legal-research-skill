from __future__ import annotations

import contextlib
import os
import subprocess
import sys
import time

import pytest

from legal_research_skill.word import processes

pytestmark = pytest.mark.skipif(not processes.is_windows(), reason="Real Win32 process APIs require Windows.")


@contextlib.contextmanager
def _disposable_process():
    """A short-lived, throwaway child process safe to query and terminate.

    Using a process we deliberately spawned (never a Word process or any
    unrelated system process) lets these tests exercise the *real* Win32
    API bodies in processes.py -- OpenProcess, GetExitCodeProcess,
    GetProcessTimes, QueryFullProcessImageNameW, TerminateProcess -- without
    any risk to the host system or a real user session.
    """
    proc = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(30)"])
    try:
        time.sleep(0.2)  # let it fully start before querying
        yield proc
    finally:
        if proc.poll() is None:
            proc.kill()
        proc.wait(timeout=5)


def test_is_process_running_true_for_self():
    assert processes.is_process_running(os.getpid()) is True


def test_is_process_running_reflects_real_child_process_lifecycle():
    with _disposable_process() as proc:
        assert processes.is_process_running(proc.pid) is True


def test_query_process_image_returns_python_executable_for_self():
    image = processes._query_process_image(os.getpid())
    assert image is not None
    assert image.lower().endswith(("python.exe", "pythonw.exe"))


def test_process_creation_time_returns_a_plausible_recent_timestamp():
    with _disposable_process() as proc:
        created = processes.process_creation_time(proc.pid)
        assert created is not None
        # Created within the last few minutes of "now", not zero/garbage.
        assert abs(time.time() - created) < 300


def test_process_creation_time_returns_none_for_a_pid_that_does_not_exist():
    # A PID far outside any plausible live range on a normal test machine.
    assert processes.process_creation_time(999_999_999) is None


def test_terminate_owned_process_actually_terminates_a_real_disposable_process():
    proc = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(30)"])
    time.sleep(0.2)
    try:
        result = processes.terminate_owned_process(proc.pid, ownership_verified=True)
        assert result["status"] == "owned_word_process_terminated"
        assert result["running_before"] is True
        assert result["running_after"] is False
        proc.wait(timeout=5)
    finally:
        if proc.poll() is None:
            proc.kill()
            proc.wait(timeout=5)


def test_terminate_owned_process_reports_not_found_for_nonexistent_pid():
    result = processes.terminate_owned_process(999_999_999, ownership_verified=True)
    assert result["status"] == "owned_word_process_not_found"
    assert result["running_before"] is False


def test_find_new_owned_word_processes_real_snapshot_finds_nothing_new_with_no_word_running():
    # No mocking: takes a real snapshot via winword_pids(). On a machine
    # with no Word process running, this must be empty and safe.
    before = processes.winword_pids()
    candidates = processes.find_new_owned_word_processes(before)
    assert candidates == []
