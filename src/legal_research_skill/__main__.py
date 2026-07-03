from __future__ import annotations

import sys


def run() -> int:
    """Entry point used by both `python -m legal_research_skill` and the
    `legal-research-skill` console script.

    The import of `legal_research_skill.cli` (and everything it pulls in,
    including the required `jsonschema` dependency) is deferred to inside
    this function and guarded, so a missing required dependency produces a
    clean, structured error message and a distinct exit code instead of a
    raw ImportError traceback. A normal `pip install` always pulls in
    `jsonschema` per the package's declared dependencies; this only matters
    if a dependency was removed or is unavailable after installation.
    """
    try:
        from legal_research_skill.cli import main
    except ImportError as exc:
        print(
            f"legal_research_skill failed to start: a required dependency is missing ({exc}). "
            "Reinstall the package with its declared dependencies, e.g. `pip install arabic-legal-research-skill`.",
            file=sys.stderr,
        )
        return 3
    return main()


if __name__ == "__main__":
    raise SystemExit(run())
