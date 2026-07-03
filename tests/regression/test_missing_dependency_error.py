from __future__ import annotations

import subprocess
import sys


def test_run_reports_missing_dependency_cleanly_instead_of_raw_traceback():
    # Run in a fully separate process: poisoning sys.modules in-process (even
    # with monkeypatch) leaks a stale legal_research_skill.loader module
    # object across other tests that already imported it at collection time,
    # silently breaking unrelated assertions elsewhere in the suite.
    script = (
        "import sys\nsys.modules['jsonschema'] = None\nfrom legal_research_skill.__main__ import run\nsys.exit(run())\n"
    )
    result = subprocess.run(
        [sys.executable, "-c", script],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 3
    assert "required dependency is missing" in result.stderr
    assert "Traceback" not in result.stderr
    assert "Traceback" not in result.stdout


def test_run_succeeds_normally_when_dependencies_are_present():
    result = subprocess.run(
        [sys.executable, "-m", "legal_research_skill", "--help"],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 0
    assert "validate" in result.stdout
