from enum import StrEnum


class Decision(StrEnum):
    PROCEED = "PROCEED"
    REVISE = "REVISE"
    PAUSE = "PAUSE"
    FAIL = "FAIL"


class FindingStatus(StrEnum):
    PASS = "pass"
    FAIL = "fail"
    WARNING = "warning"
    SKIPPED = "skipped"


class Severity(StrEnum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"
