from __future__ import annotations

import ctypes
import os
import platform
from ctypes import wintypes
from dataclasses import dataclass
from pathlib import Path
from typing import Any

PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
PROCESS_TERMINATE = 0x0001
SYNCHRONIZE = 0x00100000
STILL_ACTIVE = 259
WAIT_OBJECT_0 = 0
WAIT_TIMEOUT = 258


@dataclass(frozen=True, slots=True)
class ProcessIdentity:
    pid: int
    executable_path: str | None
    executable_name: str | None
    existed_before_dispatch: bool | None
    ownership_verified: bool
    verification_error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "pid": self.pid,
            "executable_path": self.executable_path,
            "executable_name": self.executable_name,
            "existed_before_dispatch": self.existed_before_dispatch,
            "ownership_verified": self.ownership_verified,
            "verification_error": self.verification_error,
        }


def is_windows() -> bool:
    return platform.system().lower() == "windows"


def current_pid() -> int:
    return os.getpid()


def process_snapshot() -> dict[int, dict[str, str | None]]:
    if not is_windows():
        return {}
    pids = _enum_processes()
    return {pid: {"executable_path": _query_process_image(pid), "executable_name": _process_name(pid)} for pid in pids}


def word_pid_from_hwnd(hwnd: int | None) -> int | None:
    if not is_windows() or not hwnd:
        return None
    pid = wintypes.DWORD(0)
    ctypes.windll.user32.GetWindowThreadProcessId(wintypes.HWND(int(hwnd)), ctypes.byref(pid))
    return int(pid.value) or None


def identify_word_process(pid: int | None, before_snapshot: dict[int, dict[str, str | None]]) -> ProcessIdentity | None:
    if pid is None:
        return None
    executable_path = _query_process_image(pid) if is_windows() else None
    executable_name = Path(executable_path).name if executable_path else None
    existed_before = pid in before_snapshot if before_snapshot else None
    expected_executable = executable_name is not None and executable_name.casefold() == "winword.exe"
    verified = bool(expected_executable and existed_before is False)
    error = None if verified else "Word PID ownership could not be fully verified."
    return ProcessIdentity(
        pid=pid,
        executable_path=executable_path,
        executable_name=executable_name,
        existed_before_dispatch=existed_before,
        ownership_verified=verified,
        verification_error=error,
    )


def is_process_running(pid: int | None) -> bool | None:
    if pid is None or not is_windows():
        return None
    handle = _open_process(PROCESS_QUERY_LIMITED_INFORMATION, pid)
    if not handle:
        return False
    try:
        exit_code = wintypes.DWORD(0)
        if not ctypes.windll.kernel32.GetExitCodeProcess(handle, ctypes.byref(exit_code)):
            return None
        return int(exit_code.value) == STILL_ACTIVE
    finally:
        ctypes.windll.kernel32.CloseHandle(handle)


def terminate_owned_process(pid: int | None, ownership_verified: bool) -> dict[str, Any]:
    if pid is None:
        return {"status": "owned_word_process_not_found", "pid": None, "running_after": None}
    if not ownership_verified:
        return {
            "status": "word_process_ownership_unverified",
            "pid": pid,
            "running_after": is_process_running(pid),
        }
    if not is_windows():
        return {"status": "cleanup_failed", "pid": pid, "error": "Windows process APIs are unavailable."}
    before = is_process_running(pid)
    if before is False:
        return {"status": "owned_word_process_not_found", "pid": pid, "running_before": False, "running_after": False}
    handle = _open_process(PROCESS_TERMINATE | SYNCHRONIZE | PROCESS_QUERY_LIMITED_INFORMATION, pid)
    if not handle:
        return {"status": "cleanup_failed", "pid": pid, "running_before": before, "error": "OpenProcess failed."}
    try:
        if not ctypes.windll.kernel32.TerminateProcess(handle, 1):
            return {
                "status": "cleanup_failed",
                "pid": pid,
                "running_before": before,
                "error": "TerminateProcess failed.",
            }
        wait = ctypes.windll.kernel32.WaitForSingleObject(handle, 3000)
        running_after = is_process_running(pid)
        status = (
            "owned_word_process_terminated" if wait == WAIT_OBJECT_0 and running_after is False else "cleanup_failed"
        )
        return {"status": status, "pid": pid, "running_before": before, "running_after": running_after}
    finally:
        ctypes.windll.kernel32.CloseHandle(handle)


def _open_process(access: int, pid: int):
    if not is_windows():
        return None
    return ctypes.windll.kernel32.OpenProcess(access, False, int(pid))


def _query_process_image(pid: int) -> str | None:
    handle = _open_process(PROCESS_QUERY_LIMITED_INFORMATION, pid)
    if not handle:
        return None
    try:
        size = wintypes.DWORD(32768)
        buffer = ctypes.create_unicode_buffer(size.value)
        if ctypes.windll.kernel32.QueryFullProcessImageNameW(handle, 0, buffer, ctypes.byref(size)):
            return buffer.value
    finally:
        ctypes.windll.kernel32.CloseHandle(handle)
    return None


def _process_name(pid: int) -> str | None:
    image = _query_process_image(pid)
    return Path(image).name if image else None


def _enum_processes() -> set[int]:
    psapi = ctypes.windll.psapi
    size = 4096
    while True:
        array = (wintypes.DWORD * size)()
        needed = wintypes.DWORD(0)
        if not psapi.EnumProcesses(ctypes.byref(array), ctypes.sizeof(array), ctypes.byref(needed)):
            return set()
        count = needed.value // ctypes.sizeof(wintypes.DWORD)
        if count < size:
            return {int(array[index]) for index in range(count) if int(array[index]) > 0}
        size *= 2
