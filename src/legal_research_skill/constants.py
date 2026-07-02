from pathlib import Path

PACKAGE_VERSION = "0.3.0"
SUPPORTED_RESEARCH_SCHEMA_VERSION = "0.3.0"
REPORT_SCHEMA_VERSION = "0.3.0"

PROJECT_ROOT = Path(__file__).resolve().parents[2]
WORKTREE_SCHEMAS_DIR = PROJECT_ROOT / "schemas"
PACKAGE_SCHEMAS_DIR = Path(__file__).resolve().parent / "schemas"
SCHEMAS_DIR = WORKTREE_SCHEMAS_DIR if WORKTREE_SCHEMAS_DIR.exists() else PACKAGE_SCHEMAS_DIR
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
