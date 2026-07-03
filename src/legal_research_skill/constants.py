import os
import sys
from pathlib import Path

PACKAGE_VERSION = "0.3.0"
REPORT_SCHEMA_VERSION = "0.3.0"

PROJECT_ROOT = Path(__file__).resolve().parents[2]
WORKTREE_SCHEMAS_DIR = PROJECT_ROOT / "schemas"
PACKAGE_SCHEMAS_DIR = Path(__file__).resolve().parent / "schemas"
WORKTREE_SCHEMAS_OVERRIDE_ENV_VAR = "LEGAL_RESEARCH_SKILL_USE_WORKTREE_SCHEMAS"


def resolve_schemas_dir(
    *,
    project_root: Path = PROJECT_ROOT,
    worktree_schemas_dir: Path = WORKTREE_SCHEMAS_DIR,
    package_schemas_dir: Path = PACKAGE_SCHEMAS_DIR,
    environ: dict[str, str] | None = None,
) -> Path:
    """Select the schemas directory this process should load schemas from.

    Safe/default mode always uses the schemas shipped inside the installed
    package (``package_schemas_dir``). Overriding with a repo-root
    ``schemas/`` directory (useful during local development so schema edits
    take effect without reinstalling) requires explicitly setting
    ``LEGAL_RESEARCH_SKILL_USE_WORKTREE_SCHEMAS=1`` *and* passes a sanity
    check that ``project_root`` looks like a genuine checkout of this
    project (a ``pyproject.toml`` next to the candidate ``schemas/`` dir).

    Threat model this closes: naive path-existence-based overriding (walking
    two parents above an installed package looking for a ``schemas/``
    directory) is unsafe once installed, because that ancestor location is
    unrelated to this project in an installed layout -- any unrelated
    ``schemas/`` directory placed there (nested venv, monorepo, etc.) would
    silently and unverifiably replace the packaged, tested schemas, with no
    hash check, no logging, and no way to disable it. Requiring an explicit
    opt-in environment variable plus a ``pyproject.toml`` sanity check means
    the override can never activate silently in a normal installed
    deployment, only when a developer deliberately asks for it while sitting
    in an actual source checkout.
    """
    env = environ if environ is not None else os.environ
    if env.get(WORKTREE_SCHEMAS_OVERRIDE_ENV_VAR) != "1":
        return package_schemas_dir
    looks_like_checkout = (project_root / "pyproject.toml").is_file() and worktree_schemas_dir.is_dir()
    if not looks_like_checkout:
        return package_schemas_dir
    print(
        f"[legal_research_skill] Using worktree schemas from {worktree_schemas_dir} "
        f"({WORKTREE_SCHEMAS_OVERRIDE_ENV_VAR}=1).",
        file=sys.stderr,
    )
    return worktree_schemas_dir


SCHEMAS_DIR = resolve_schemas_dir()
RESEARCH_STATE_SCHEMA = SCHEMAS_DIR / "research-state.schema.json"
VALIDATION_REPORT_SCHEMA = SCHEMAS_DIR / "validation-report.schema.json"
ARTIFACT_MANIFEST_SCHEMA = SCHEMAS_DIR / "artifact-manifest.schema.json"

ALLOWED_HIERARCHY = ("part", "chapter", "section", "subsection", "demand")
HIERARCHY_LABELS = {
    "part": "قسم",
    "chapter": "باب",
    "section": "فصل",
    "subsection": "مبحث",
    "demand": "مطلب",
}

DECISION_ORDER = {"PROCEED": 0, "REVISE": 1, "PAUSE": 2, "FAIL": 3}
STATUS_ORDER = {"pass": 0, "skipped": 1, "warning": 2, "fail": 3}
SEVERITY_ORDER = {"info": 0, "low": 1, "medium": 2, "high": 3, "critical": 4}
